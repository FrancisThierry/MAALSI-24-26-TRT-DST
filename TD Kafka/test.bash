# Entrer dans le conteneur Kafka
docker exec -it kafka bash

# Créer un topic pour le test
kafka-topics --create --topic test-topic --bootstrap-server localhost:29092 --partitions 1 --replication-factor 1

# Vérifier que le topic a été créé
kafka-topics --list --bootstrap-server localhost:29092
# Quitter le conteneur
exit