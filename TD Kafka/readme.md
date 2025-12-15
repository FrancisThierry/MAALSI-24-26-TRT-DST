

## 📝 Cahier des Charges (Objectif du TD)

L'objectif principal de ce TD est de mettre en place une architecture basée sur les événements (Event-Driven Architecture) en utilisant Kafka pour simuler le cycle de vie d'une entité métier complexe.

### Entité Simmulée : La Demande de Voyage (DV)

Le cycle de vie d'une Demande de Voyage est décomposé en une série d'événements, stockés de manière fiable et ordonnée.

| Rôle du Flux de Données | Description |
| :--- | :--- |
| **But Principal** | Gérer les transitions d'état d'une Demande de Voyage (DV) en temps réel. |
| **Source de Vérité** | Kafka est la **source de vérité** temporaire. L'état actuel de la DV doit être reconstruit en lisant l'historique de tous les événements liés à cette DV. |
| **Cycle de Vie Modélisé** | `CREATION` $\rightarrow$ `EN\_ATTENTE\_VALIDATION` $\rightarrow$ `VALIDEE` $\rightarrow$ `PLANIFIEE` $\rightarrow$ `DEPART` $\rightarrow$ `RETOUR` $\rightarrow$ `CLOTUREE` |
| **Gestion des Anomalies** | Inclure des événements dits "anormaux" comme `RETARD` ou `ANNULATION`, qui peuvent survenir à tout moment et modifier l'état. |

---

## 🏗️ Architecture et Rôles des Composants

Votre infrastructure est composée de trois services Docker et de deux applications Python.

### A. Les Services Docker (Infrastructure)

| Service | Rôle Principal | Détail Technique |
| :--- | :--- | :--- |
| **`zookeeper`** | Chef d'orchestre | Service historique nécessaire à Kafka pour gérer la configuration, les métadonnées, et le statut des brokers et des consommateurs. |
| **`kafka`** | Broker / Journal d'Événements | Le cœur du système. Il reçoit les événements, les stocke de manière durable dans le **Topic** (`demande-voyage`), et les distribue aux consommateurs abonnés. |
| **`kafka-ui`** | Outil d'Administration | Interface web pour visualiser le trafic. Permet de s'assurer que les Topics existent et que les messages y sont correctement publiés. |

### B. Les Scripts Python (Applications Métier)

| Script | Rôle Kafka | Rôle Métier |
| :--- | :--- | :--- |
| **`producer_voyage.py`** | Producteur Kafka | **Simule l'émetteur de l'événement** (l'employé, le manager, l'agent de voyage, ou le système de réservation). Il envoie un message au Topic `demande-voyage` à chaque changement d'état (ex: la demande passe à `VALIDEE`). |
| **`consumer_voyage.py`** | Consommateur Kafka | **Simule le système de gestion central** (le tableau de bord, la base de données de suivi). Il s'abonne au Topic `demande-voyage`, lit les messages en temps réel, et met à jour l'état actuel de chaque DV dans un dictionnaire en mémoire. |

---

## 🔎 Ce que fait chaque Script Python en Détail

### 1. `producer_voyage.py` (L'émetteur du changement)

* **Connexion :** Se connecte au Kafka Broker sur l'adresse externe `localhost:9092`.
* **Sérialisation :** Convertit les dictionnaires Python des événements en format JSON encodé (`value_serializer=lambda v: json.dumps(v).encode('utf-8')`) pour l'envoi.
* **Envoi Sérialisé :** Envoie les messages (événements) au Topic `demande-voyage`.
* **Garantie d'Ordre :** Il utilise l'ID de la demande de voyage (`REQUEST_ID`) comme **clé Kafka** (`key=key`). Cela garantit que tous les événements d'une seule demande (`DV-2025-003`) iront dans la même partition Kafka et seront donc lus **dans l'ordre chronologique** par le consommateur, ce qui est crucial pour reconstruire l'état.

### 2. `consumer_voyage.py` (Le récepteur et agrégateur d'état)

* **Connexion & Abonnement :** Se connecte au Broker et s'abonne au Topic `demande-voyage` avec un `group_id` unique (`gestion-voyage-service`).
* **Désérialisation :** Reçoit les messages JSON encodés de Kafka et les reconvertit en dictionnaires Python.
* **Traitement (Event Sourcing simplifié) :** Pour chaque événement reçu :
    * Il extrait l'ID de la demande et le nouvel état (`etat`).
    * Il met à jour le dictionnaire `current_states` : l'état actuel de la DV est remplacé par le dernier événement reçu.
    * **Résultat :** Le Consommateur maintient en temps réel une vue consolidée (le "tableau de bord") de l'état actuel de toutes les Demandes de Voyage. 



