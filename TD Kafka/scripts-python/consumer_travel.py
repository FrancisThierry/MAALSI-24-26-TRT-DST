import json
from kafka import KafkaConsumer

# Configuration
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'demande-voyage'

# Dictionnaire pour stocker l'état actuel de toutes les demandes de voyage (Event Sourcing simplifié)
current_states = {}

# Initialisation du Consommateur
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BROKER],
    # Commence au plus vieux message si c'est la première fois ou si l'offset est perdu
    auto_offset_reset='earliest', 
    enable_auto_commit=True,
    # group_id permet à Kafka de savoir quel consommateur a déjà lu quels messages
    group_id='gestion-voyage-service',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print(f"👂 Consommateur démarré. Écoute sur le topic '{TOPIC_NAME}'...")
print("=" * 70)

# Traitement des messages en continu
for message in consumer:
    event = message.value
    dv_id = event['id']
    new_state = event['etat']
    
    # 1. Mise à jour de l'état central
    current_states[dv_id] = new_state
    
    # 2. Affichage de l'événement reçu
    print(f"*** Événement Reçu ***")
    print(f"| ID: {dv_id}")
    print(f"| NOUVEL ÉTAT: {new_state}")
    print(f"| Détails : {event['details']}")
    
    # 3. Affichage du Tableau de bord (l'état actuel de tous les DV)
    print("\n--- Tableau de Bord des DV (États Actuels) : ---")
    for id, state in current_states.items():
        print(f"   [ {id} ] est actuellement : {state}")
    print("=" * 70)