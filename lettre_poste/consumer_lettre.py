import time
from kafka import KafkaConsumer
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration de Kafka
KAFKA_SERVER = 'localhost:9092' # Remplacez si votre serveur est ailleurs
TOPIC_NAME = 'evenements_lettres'
GROUP_ID = 'groupe-suivi-lettres' # Identifiant du groupe de consommateurs

# Initialiser le consommateur
# value_deserializer permet de convertir les bytes reçus de Kafka en objet Python (ici un dictionnaire)
try:
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_SERVER],
        group_id=GROUP_ID,
        auto_offset_reset='earliest', # Commencez à lire depuis le début du topic si le groupe est nouveau
        enable_auto_commit=True, # Confirmer automatiquement le traitement des messages
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    logging.info(f"Consommateur Kafka démarré pour le topic '{TOPIC_NAME}'")
except Exception as e:
    logging.error(f"Erreur de connexion au consommateur : {e}")
    exit(1)

# Boucle principale de consommation
logging.info("En attente de messages... (Appuyez sur Ctrl+C pour arrêter)")
try:
    for message in consumer:
        # Le message.value est l'objet Python désérialisé (le dictionnaire d'événement)
        event = message.value
        
        # Affichage des informations
        print(f"\n--- Nouvel Événement Reçu ---")
        print(f"Topic: {message.topic}")
        print(f"Partition: {message.partition}")
        print(f"Offset: {message.offset}")
        print(f"Clé (lettre_id): {message.key.decode('utf-8') if message.key else 'N/A'}")
        
        # Affichage du statut de la lettre
        lettre_id = event.get('lettre_id', 'INCONNU')
        statut = event.get('statut', 'INCONNU')
        timestamp = event.get('timestamp')
        
        print(f"Événement: Lettre {lettre_id} - Statut : **{statut.upper()}**")
        print(f"Heure de l'événement: {time.ctime(timestamp / 1000) if timestamp else 'N/A'}")
        print("----------------------------")

except KeyboardInterrupt:
    logging.info("Arrêt du consommateur par l'utilisateur.")
finally:
    consumer.close()
    logging.info("Connexion du consommateur fermée.")