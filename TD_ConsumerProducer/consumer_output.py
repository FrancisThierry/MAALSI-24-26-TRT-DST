from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'temperatures_fahrenheit_processed',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    group_id='validation_group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("--- Lecture des résultats (Fahrenheit) ---")
for message in consumer:
    print(f"Reçu : {message.value}")