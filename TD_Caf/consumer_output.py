import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'cartes-finales',
    'alertes-rejet',
    bootstrap_servers=['localhost:9092'],
    group_id='notifications-group',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    key_deserializer=lambda x: x.decode('utf-8') if x else None
)

print("Moniteur de sortie pret...")

for msg in consumer:
    topic = msg.topic
    uid = msg.key
    
    if topic == 'cartes-finales':
        print(f"Succes : Carte generee pour {uid}")
    elif topic == 'alertes-rejet':
        print(f"Echec : Notification de refus envoyee a {uid}")