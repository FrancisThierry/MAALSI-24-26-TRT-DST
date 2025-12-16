# 1. Entrer dans le conteneur Kafka
# (Note : vérifiez le nom exact avec 'docker ps', ici on suppose 'kafka')
docker exec -it kafka bash

# 2. Créer le topic d'ENTRÉE (Réception des dossiers)
kafka-topics --create --topic demandes-cartes --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# 3. Créer le topic de REJET (Alertes Fraude/Conformité)
kafka-topics --create --topic alertes-rejet --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# 4. Créer le topic de SORTIE (Cartes validées)
kafka-topics --create --topic cartes-finales --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# 5. Vérifier la liste complète
kafka-topics --list --bootstrap-server localhost:9092

# 6. Sortir du conteneur
exit