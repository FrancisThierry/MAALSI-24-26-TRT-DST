import json
import time
from kafka import KafkaProducer

# Configuration
# Le broker est accessible via l'adresse externe exposée par Docker Compose
KAFKA_BROKER = 'localhost:9092' 
TOPIC_NAME = 'demande-voyage'
REQUEST_ID = 'DV-2025-003' # ID de la demande que nous allons suivre

# Initialisation du Producteur
# value_serializer convertit les dictionnaires Python en JSON encodé pour Kafka
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"🌍 Producteur démarré. Envoi sur le topic '{TOPIC_NAME}' pour la demande {REQUEST_ID}...")

# Définition du cycle de vie des événements
lifecycle_events = [
    # 1. CREATION
    {"id": REQUEST_ID, "etat": "CREATION", "details": {"destination": "New York", "employe": "Sophie Dupont"}},
    # 2. VALIDATION
    {"id": REQUEST_ID, "etat": "EN_ATTENTE_VALIDATION_MANAGER", "details": {"manager": "Marc Lefevre"}},
    time.sleep(2), # Simuler le temps d'attente
    {"id": REQUEST_ID, "etat": "VALIDEE", "details": {"manager": "Marc Lefevre", "budget_approuve": 1200.00}},
    # 3. PLANIFICATION
    {"id": REQUEST_ID, "etat": "PLANIFIEE", "details": {"vol": "LH987", "hotel": "Midtown Plaza", "date_depart": "2026-03-15"}},
    # 4. Événement Spécial (Retard)
    time.sleep(5), # Quelques jours après...
    {"id": REQUEST_ID, "etat": "RETARD", "details": {"cause": "Grève aérienne", "nouveau_depart": "2026-03-16 09:00"}},
    # 5. DEPART et FIN
    {"id": REQUEST_ID, "etat": "DEPART", "details": {"statut": "À l'aéroport"}},
    time.sleep(3),
    {"id": REQUEST_ID, "etat": "RETOUR", "details": {"duree_totale_jours": 4}},
    {"id": REQUEST_ID, "etat": "CLOTUREE", "details": {"frais_notes": "En attente de remboursement"}}
]

# Envoi des événements un par un
for event in lifecycle_events:
    if event is None: continue # Ignorer les time.sleep()
    
    key = event['id'].encode('utf-8') # Clé = ID de la DV (assure l'ordre des messages pour cette DV)
    
    print(f"\n-> Envoi Événement : ID={event['id']}, ETAT={event['etat']}")
    producer.send(TOPIC_NAME, key=key, value=event)
    
    time.sleep(1.5) # Pause entre les événements
    
# Finalisation
producer.flush()
print("\n✅ Simulation du Producteur terminée. Tous les événements ont été envoyés.")