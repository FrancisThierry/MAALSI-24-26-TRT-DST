import json
import time
from kafka import KafkaConsumer

# Configuration
TOPIC_NAME = 'gestion-machines'
BOOTSTRAP_SERVERS = ['localhost:9092']

# Initialisation du Consommateur
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id='factory-monitor-group',
    auto_offset_reset='earliest',
    enable_auto_commit=False,       # CRUCIAL : On commit manuellement
    max_poll_records=1,             # On traite un seul message à la fois
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def process_order(order_data):
    """Simule le temps de travail de la machine"""
    etape = order_data['etape']
    machine = order_data['machine']
    action = order_data['action']
    
    print(f"\n[DÉBUT] {machine} commence l'étape {etape}...")
    print(f"Instruction : {action}")
    
    # Simulation du temps de production (3 secondes)
    time.sleep(3)
    
    print(f"[TERMINÉ] {machine} a fini l'étape {etape}.")

print(f"En attente d'ordres sur le topic '{TOPIC_NAME}'...")

try:
    for message in consumer:
        order = message.value
        
        # 1. Exécution du travail
        process_order(order)
        
        # 2. Point de contrôle : On ne commit que si le travail est fini
        consumer.commit()
        print(f"--- Offset {message.offset} commité avec succès ---")

except KeyboardInterrupt:
    print("\nArrêt du consommateur...")
finally:
    consumer.close()