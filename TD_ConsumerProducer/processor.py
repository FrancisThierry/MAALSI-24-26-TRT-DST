import json
import time
from kafka import KafkaConsumer, KafkaProducer

# 1. Configuration du Consommateur
consumer = KafkaConsumer(
    'temperatures_celsius_raw',
    bootstrap_servers=['localhost:9092'],
    group_id='temp_converter_group',
    auto_offset_reset='earliest', # Lit depuis le début si aucun offset n'est enregistré
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8') if k else None
)

# 2. Configuration du Producteur
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("--- Processor en attente de messages... ---")

try:
    for message in consumer:
        try:
            # Extraction des données
            sensor_id = message.key
            data = message.value
            
            # Transformation (Celsius vers Fahrenheit)
            celsius = data['celsius']
            fahrenheit = celsius * 1.8 + 32
            
            # Construction du message de sortie
            output_payload = {
                "sensor_id": sensor_id,
                "location": data['location'],
                "fahrenheit": round(fahrenheit, 2),
                "processed_timestamp": time.time(),
                "source_topic": "temperatures_celsius_raw"
            }
            
            # Envoi vers le topic de sortie
            producer.send('temperatures_fahrenheit_processed', key=sensor_id, value=output_payload)
            print(f"Transformé : {sensor_id} | {celsius}°C -> {fahrenheit}°F")
            
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"Erreur de traitement sur le message : {e}")
            continue # Passe au message suivant sans crasher

except KeyboardInterrupt:
    print("Arrêt du Processor...")
finally:
    consumer.close()
    producer.close()