import json
from kafka import KafkaConsumer, KafkaProducer

# Configuration du producteur pour les sorties
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8')
)

# Configuration du consommateur
consumer = KafkaConsumer(
    'demandes-cartes',
    bootstrap_servers=['localhost:9092'],
    group_id='nacaire-processor-group',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    key_deserializer=lambda x: x.decode('utf-8') if x else None
)

# Stockage de l'etat en memoire
etats_utilisateurs = {}

print("Processeur NACAIRE en attente de messages...")

for msg in consumer:
    evt = msg.value
    uid = evt['id_utilisateur']
    
    # Initialisation de l'etat si inconnu
    if uid not in etats_utilisateurs:
        etats_utilisateurs[uid] = {"SOCIAL": "EN_COURS", "KYC": "EN_COURS", "FINAL": "EN_COURS"}

    # Mise a jour selon l'evenement
    if evt['type_evenement'] in ["SOCIAL", "KYC"]:
        etats_utilisateurs[uid][evt['type_evenement']] = evt['statut']

    etat = etats_utilisateurs[uid]

    # Logique de decision
    if etat["FINAL"] == "EN_COURS":
        # Regle de rejet
        if etat["SOCIAL"] == "REFUSE" or etat["KYC"] == "REFUSE":
            etat["FINAL"] = "REFUSEE"
            producer.send('alertes-rejet', key=uid, value=etat)
            print(f"Decision : Utilisateur {uid} REFUSE")
        
        # Regle d'acceptation
        elif etat["SOCIAL"] == "ACCEPTE" and etat["KYC"] == "ACCEPTE":
            etat["FINAL"] = "EN_LIGNE"
            producer.send('cartes-finales', key=uid, value=etat)
            print(f"Decision : Utilisateur {uid} ACCEPTE")
    
    producer.flush()