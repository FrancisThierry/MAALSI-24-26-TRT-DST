import json
import time
from kafka import KafkaProducer

# Configuration du producteur
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8')
)

def envoyer_evt(user_id, type_evt, statut):
    data = {
        "id_utilisateur": user_id,
        "type_evenement": type_evt,
        "statut": statut,
        "timestamp": time.time()
    }
    
    # Envoi du message au topic 'demandes-cartes'
    producer.send('demandes-cartes', key=user_id, value=data)
    print(f"Evenement envoye : {user_id} - {type_evt} - {statut}")
    producer.flush()

if __name__ == "__main__":
    print("Demarrage de la simulation NACAIRE...")
    
    # Scenario 1 : Dossier valide
    print("Utilisateur 001 : Parcours succes")
    envoyer_evt("user_001", "INITIALISATION", "EN_COURS")
    time.sleep(1)
    envoyer_evt("user_001", "SOCIAL", "ACCEPTE")
    time.sleep(1)
    envoyer_evt("user_001", "KYC", "ACCEPTE")

    # Scenario 2 : Dossier refuse
    print("Utilisateur 002 : Rejet KYC")
    envoyer_evt("user_002", "SOCIAL", "ACCEPTE")
    envoyer_evt("user_002", "KYC", "REFUSE")