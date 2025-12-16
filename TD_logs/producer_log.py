import json
import time
from kafka import KafkaProducer

# Configuration
# Le broker est accessible via l'adresse externe exposée par Docker Compose
KAFKA_BROKER = 'localhost:9092' 
TOPIC_NAME = 'gestion-logs'
REQUEST_ID = 'LOG-2025-003' # ID de la demande que nous allons suivre

# Initialisation du Producteur
# value_serializer convertit les dictionnaires Python en JSON encodé pour Kafka
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

log_events = [
    {"ip": "192.168.1.10", "user": "user_a", "date": "16/Dec/2025:10:30:01 +0100", "method": "GET", "url": "/index.html", "http_version": "HTTP/1.1", "status_code": 200, "size": 1250, "referrer": "-", "user_agent": "Mozilla/5.0"},
    {"ip": "192.168.1.10", "user": "user_a", "date": "16/Dec/2025:10:30:10 +0100", "method": "GET", "url": "/config.json", "http_version": "HTTP/1.1", "status_code": 404, "size": 150, "referrer": "-", "user_agent": "Wget"},
    {"ip": "192.168.1.10", "user": "user_a", "date": "16/Dec/2025:10:30:15 +0100", "method": "POST", "url": "/submit/form", "http_version": "HTTP/1.1", "status_code": 500, "size": 500, "referrer": "-", "user_agent": "PHP-Client"},
    {"ip": "192.168.1.20", "user": "user_c", "date": "16/Dec/2025:10:30:12 +0100", "method": "GET", "url": "/secure/page", "http_version": "HTTP/1.1", "status_code": 401, "size": 250, "referrer": "-", "user_agent": "Mozilla/5.0"},
    {"ip": "192.168.1.1", "user": "admin", "date": "16/Dec/2025:10:30:25 +0100", "method": "DELETE", "url": "/resource/123", "http_version": "HTTP/1.1", "status_code": 500, "size": 50, "referrer": "-", "user_agent": "Custom-App"},
    {"ip": "172.16.0.10", "user": "user_d", "date": "16/Dec/2025:10:30:20 +0100", "method": "GET", "url": "/images/logo.png", "http_version": "HTTP/1.1", "status_code": 200, "size": 45000, "referrer": "http://site.com/", "user_agent": "Chrome"}
]

# Envoi des événements un par un
for event in log_events:
    if event is None: continue
    key = event['ip'].encode('utf-8') # Clé = IP de l'utilisateur (assure l'ordre des messages pour cet utilisateur)
    print(f"\n-> Envoi Événement : IP={event['ip']}, date={event['date']}")
    producer.send(TOPIC_NAME, key=key, value=event)
    time.sleep(1)
