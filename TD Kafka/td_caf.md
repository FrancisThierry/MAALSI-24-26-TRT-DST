

# 🎓 Présentation du Travail Dirigé : Architecture Événementielle pour l'Éligibilité aux Aides Sociales

## Partie 1 : Contexte et Problématique Métier

### 1.1 Contexte de l'Organisme NACAIRE

L'organisme **NACAIRE** (similaire à une CAF) gère l'accès à une carte de réduction sociale pour des centaines de milliers de foyers, impliquant des flux financiers importants (plusieurs milliards d'euros de prestations annuelles).

* **Le Produit :** Une carte de réduction sociale, nécessitant une double validation rigoureuse (Dossier Social et Conformité Bancaire).
* **L'Enjeu :** La rapidité de traitement (impact social) et la fiabilité des contrôles (lutte contre la fraude et conformité LCB/FT).

### 1.2 La Problématique des Anciens Systèmes

Historiquement, le traitement est **séquentiel et synchrone** :
1.  Soumission du dossier.
2.  Attente que le Dossier Principal soit validé.
3.  Si validé, lancement de la vérification KYC.
4.  Si un élément est incomplet, tout le processus s'arrête.

**Objectif de la Modernisation :** Passer à un traitement **parallèle et asynchrone** pour accélérer le temps de réponse et permettre une gestion modulaire.

## Partie 2 : La Solution Technique (Architecture Événementielle)

Nous avons mis en place une **Architecture Orientée Événements (EDA)** basée sur Kafka et orchestrée par Docker, qui modélise le processus comme un flux continu de changements. 

### 2.1 Infrastructure Technique (Docker)

L'environnement est déployé localement via `docker compose` :

| Service | Rôle Technique | Justification |
| :--- | :--- | :--- |
| **`zookeeper`** | Gestion de l'état du cluster. | Composant requis par Kafka pour la découverte des services. |
| **`kafka`** | Broker central. | Stockage durable et ordonné de tous les événements de l'utilisateur. |
| **`kafka-ui`** | Monitoring. | Visualisation du trafic en temps réel pour validation et débogage. |

### 2.2 Modélisation du Flux par Topics

Le flux de données est organisé autour de trois topics principaux :

| Topic | Fonction | Acteurs |
| :--- | :--- | :--- |
| **`demandes-cartes`** | **Topic d'entrée.** Reçoit tous les événements de mise à jour des sous-dossiers (Social et KYC). | Producteur (Portail utilisateur, Service KYC). |
| **`alertes-rejet`** | **Topic de notification.** Publie les rejets immédiats (Fraude, Dossier principal refusé). | Consumer Processor. |
| **`cartes-finales`** | **Topic de sortie.** Publie l'événement de délivrance de la carte (`EN_LIGNE`). | Consumer Processor. |

### 2.3 Rôles des Applications Python (Microservices)

| Script/Rôle | Type Kafka | Fonction Métier |
| :--- | :--- | :--- |
| **`producteur_demandes.py`** | Producteur | **Simule les sources de données :** Envoie les événements d'initialisation et de mise à jour (ex: "KYC\_ACCEPTE" ou "DOSSIER\_REFUSE") sur `demandes-cartes`. |
| **`consumer_processor.py`** | Consommateur/Producteur | **Cœur de la Logique de Décision :** Maintient l'état complet de l'utilisateur (Event Sourcing) et applique la règle de validation croisée. |
| **`consumer_final.py`** | Consommateur | **Moniteur de Production :** Écoute les topics finaux pour imprimer la carte ou envoyer la notification de rejet. |

## Partie 3 : La Logique de Décision (Rôle du Processor)

Le challenge principal réside dans la logique intégrée au `consumer_processor.py`. Ce service doit être capable de gérer l'état de l'utilisateur de manière fiable, même si les événements arrivent dans le désordre (ce qui est possible dans un système asynchrone).

### 3.1 La Gestion de l'État (Event Sourcing)

Le Processor utilise l'**`id_utilisateur`** comme clé pour stocker l'état actuel de l'utilisateur :
$$
\text{État Global} = \{ \text{Dossier Principal}, \text{KYC}, \text{Carte} \}
$$
Grâce à la clé Kafka, tous les événements d'un même utilisateur sont traités dans le bon ordre, permettant au Processor de toujours connaître le dernier statut reçu pour chaque sous-dossier.

### 3.2 La Règle d'Or de la Conformité

Le Processor applique la règle de la double-validation :

1.  **Rejet Implacable :** Si un événement de rejet (`REFUSE` ou `FRAUDE_DETECTEE`) est reçu sur l'un des deux sous-dossiers, l'état final passe immédiatement à `REFUSEE`.
2.  **Validation Finale :** L'événement final de délivrance est publié uniquement lorsque la condition de succès est remplie :

$$
\text{Carte EN\_LIGNE} \iff (\text{Dossier Principal} = \text{ACCEPTE}) \land (\text{KYC} = \text{ACCEPTE})
$$

### 3.3 Démonstration du Scénario (Exemple)

| Événement Reçu (Producteur) | Dossier Principal | KYC | État Final de la Carte | Action du Processor |
| :--- | :--- | :--- | :--- | :--- |
| INITIALISATION | EN\_COURS | EN\_COURS | EN\_COURS | Initier l'état. |
| KYC\_ACCEPTE | EN\_COURS | ACCEPTE | EN\_COURS | Le Processor attend le Dossier Principal. |
| DOSSIER\_PRINCIPAL\_ACCEPTE | ACCEPTE | ACCEPTE | **EN\_LIGNE** | **Condition remplie.** Publication sur `cartes-finales`. |
| *--OU--* | | | | |
| DOSSIER\_PRINCIPAL\_REFUSE | REFUSE | EN\_COURS | **REFUSEE** | **Rejet immédiat.** Publication sur `alertes-rejet`. |

## Adapter le programme
Adapter le programme pour recevoir en entrée, un fichier csv et en sortie un fichier csv également.

```csv

id_utilisateur,type_evenement,statut
user_003,INITIALISATION,EN_COURS
user_003,SOCIAL,ACCEPTE
user_003,KYC,ACCEPTE
user_004,INITIALISATION,EN_COURS
user_004,SOCIAL,REFUSE
user_004,KYC,ACCEPTE
user_005,INITIALISATION,EN_COURS
user_005,SOCIAL,ACCEPTE
user_005,KYC,REFUSE
user_006,INITIALISATION,EN_COURS
user_006,SOCIAL,ACCEPTE
user_006,KYC,ACCEPTE
user_007,INITIALISATION,EN_COURS
user_007,SOCIAL,REFUSE
user_008,INITIALISATION,EN_COURS
user_008,SOCIAL,ACCEPTE
user_008,KYC,ACCEPTE
user_009,INITIALISATION,EN_COURS
user_009,SOCIAL,EN_COURS
user_010,KYC,REFUSE
```
