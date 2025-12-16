from kafka import KafkaProducer
import json
import time
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration de Kafka
KAFKA_SERVER = 'localhost:9092'  # Remplacez si votre serveur est ailleurs
TOPIC_NAME = 'evenements_lettres'

# Initialiser le producteur
# value_serializer permet de convertir l'objet Python (ici un dictionnaire) en bytes pour Kafka
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logging.info(f"Producteur Kafka connecté à {KAFKA_SERVER}")
except Exception as e:
    logging.error(f"Erreur de connexion au producteur : {e}")
    exit(1)

# Événements à envoyer
evenements_lettre = [
    {"lettre_id": "ABC-12345", "statut": "envoyée", "timestamp": int(time.time() * 1000)},
    {"lettre_id": "ABC-12345", "statut": "reçu", "timestamp": int(time.time() * 1000) + 5000},
    {"lettre_id": "ABC-12345", "statut": "contre signé", "timestamp": int(time.time() * 1000) + 15000},
    {"lettre_id": "DEF-67890", "statut": "envoyée", "timestamp": int(time.time() * 1000) + 20000},
    {"lettre_id": "DEF-67890", "statut": "npai", "timestamp": int(time.time() * 1000) + 25000}, # N'habite Plus à l'Adresse Indiquée
]

# Fonction de callback pour la confirmation d'envoi
def on_send_success(record_metadata):
    logging.info(f"Message envoyé avec succès au topic: {record_metadata.topic}, partition: {record_metadata.partition}, offset: {record_metadata.offset}")

def on_send_error(excp):
    logging.error(f"Erreur lors de l'envoi du message : {excp}")

# Envoyer les messages
logging.info(f"Début de l'envoi des événements sur le topic '{TOPIC_NAME}'...")
for event in evenements_lettre:
    logging.info(f"Envoi de l'événement : {event['statut']} pour la lettre {event['lettre_id']}")
    
    # Utilisez 'lettre_id' comme clé pour garantir que tous les événements de la même lettre 
    # vont à la même partition (s'il y en a plusieurs), respectant l'ordre.
    future = producer.send(
        TOPIC_NAME, 
        key=event['lettre_id'].encode('utf-8'), 
        value=event
    )
    
    # Ajouter les callbacks
    future.add_callback(on_send_success).add_errback(on_send_error)
    
    # Attendre un peu avant d'envoyer le prochain événement
    time.sleep(1)

# S'assurer que tous les messages asynchrones ont été envoyés
producer.flush()
logging.info("Tous les événements ont été envoyés.")
producer.close()