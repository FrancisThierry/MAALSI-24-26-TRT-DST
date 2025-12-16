import json
import time
from kafka import KafkaProducer

# Configuration
TOPIC_NAME = 'gestion-machines'
BOOTSTRAP_SERVERS = ['localhost:9092']
WORK_LOT_KEY = b'LOT_42'

# Initialisation du Producteur avec paramètres de fiabilité
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    key_serializer=lambda k: k,  # La clé est déjà en bytes
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',                # Attendre tous les ISR
    enable_idempotence=True    # Empêcher les doublons et garantir l'ordre
)

# Liste des ordres de production
ordres = [
    {"etape": 1, "machine": "M1 : Découpe CNC", "action": "Découper la forme de base"},
    {"etape": 2, "machine": "M2 : Perçage Laser", "action": "Ajouter des trous de fixation"},
    {"etape": 3, "machine": "M3 : Finition", "action": "Polissage et nettoyage final"}
]

def send_production_orders():
    print(f"--- Début de l'envoi des ordres pour le {WORK_LOT_KEY.decode()} ---")
    
    for ordre in ordres:
        try:
            print(f"Envoi de l'étape {ordre['etape']}...")
            
            # Envoi synchrone grâce à .get()
            future = producer.send(
                topic=TOPIC_NAME,
                key=WORK_LOT_KEY,
                value=ordre
            )
            
            # Attente de la confirmation du broker avant de passer au suivant
            record_metadata = future.get(timeout=10)
            
            print(f"Confirmation : Etape {ordre['etape']} stockée "
                  f"dans partition {record_metadata.partition} "
                  f"à l'offset {record_metadata.offset}")
            
        except Exception as e:
            print(f"Erreur lors de l'envoi : {e}")
            break

    producer.flush()
    print("--- Tous les messages ont été envoyés avec succès ---")

if __name__ == "__main__":
    send_production_orders()