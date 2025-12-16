# Entrer dans le conteneur
docker exec -it kafka bash

# Créer le topic SOURCE
kafka-topics --create --topic temperatures_celsius_raw --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Créer le topic DESTINATION
kafka-topics --create --topic temperatures_fahrenheit_processed --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Vérifier la liste
kafka-topics --list --bootstrap-server localhost:9092
exit