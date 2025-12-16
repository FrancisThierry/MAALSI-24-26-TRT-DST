import json
import re
from kafka import KafkaConsumer

# Configuration
# Le broker est accessible via l'adresse externe exposée par Docker Compose
KAFKA_BROKER = 'localhost:9092' 
TOPIC_NAME = 'gestion-logs'

current_states = {}

# Initialisation du Consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='gestion-log',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


print(f" Consommateur démarré. Écoute sur le topic '{TOPIC_NAME}'...")
print("=" * 70)

# Traitement des messages en continu
for message in consumer:
    event = message.value
    
    
    ip_address = event.get('ip')
    user = event.get('user')
    date = event.get('date')
    method = event.get('method')
    url = event.get('url')
    http_version = event.get('http_version')
    status_code = event.get('status_code')
    # Mise à jour de l'état (Exemple : on stocke le dernier statut par IP)
    current_states[ip_address] = status_code
    size = event.get('size')
    referrer = event.get('referrer')
    user_agent = event.get('user_agent')
    
    # 2. Affichage de l'événement reçu
    print(f"*** Événement Reçu ***")
    print(f"| IP: {ip_address}")
    print(f"| USER: {user}")
    print(f"| DATE: {date}")
    print(f"| METHOD: {method}")
    print(f"| URL: {url}")
    print(f"| HTTP VERSION: {http_version}")
    print(f"| STATUS CODE: {status_code}")
    print(f"| SIZE: {size}")
    print(f"| REFERRER: {referrer}")
    print(f"| USER AGENT: {user_agent}")
    
    if re.match(r'^4\d{2}$|^5\d{2}$', str(status_code)):
        print(f"*** ERREUR {status_code} ***")
        print(f"*** Envoi de SMS pour avertir l'administrateur ***")
        try:
            # Envoi de SMS
            print(f"*** SMS envoyé : Simulation de l'envoi du SMS ***")
        except Exception as e:
            print(f"*** Échec de l'envoi du SMS : {str(e)} ***")
    
    # 3. Affichage du Tableau de bord (l'état actuel de tous les logs)
    print("\n--- Tableau de Bord des logs (États Actuels) : ---")
    for id, state in current_states.items():
        print(f"   [ {id} ] est actuellement : {state}")
    print("=" * 70)

