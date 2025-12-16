import json
from kafka import KafkaProducer

def on_success(record_metadata):
    print(f"Message envoyé : Topic={record_metadata.topic}, Partition={record_metadata.partition}, Offset={record_metadata.offset}")

def on_error(excp):
    print(f"Erreur lors de l'envoi : {excp}")

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

data = [
    ("SENS_A", {"id": 1, "location": "NYC", "celsius": 10.5}),
    ("SENS_B", {"id": 2, "location": "PAR", "celsius": 20.0}),
    ("SENS_A", {"id": 3, "location": "NYC", "celsius": 12.2}),
]

print("--- Démarrage du Producteur de Test ---")
for key, value in data:
    future = producer.send('temperatures_celsius_raw', key=key, value=value)
    future.add_callback(on_success).add_errback(on_error)

producer.flush() # S'assurer que tout est envoyé
producer.close()