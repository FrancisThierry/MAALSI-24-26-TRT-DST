
# 🛠️ Travaux Dirigés (TD) : Chaîne de Production Ordonnée avec Kafka (Indications Seules)

**Objectif :** Mettre en œuvre et vérifier l'ordre strict d'exécution d'une séquence de travail par trois machines-outils simulées, en utilisant un seul *topic* Kafka et la clé de message.

## 1. ⚙️ Pré-requis

1.  **Environnement :** Assurez-vous d'avoir un *broker* Kafka opérationnel (généralement sur `localhost:9092`).
2.  **Bibliothèque :** La bibliothèque Python `kafka-python` doit être installée.
3.  **Topic :** Créez un *topic* unique, par exemple : `commandes_machines_td`.

## 2. 📝 Le Scénario de Production

Simuler un processus en trois étapes strictes pour un même Lot de travail (`LOT_42`) :

| Étape | Machine | Instruction |
| :---: | :---: | :--- |
| **1** | M1 : Découpe CNC | Découper la forme de base. |
| **2** | M2 : Perçage Laser | Ajouter des trous de fixation. |
| **3** | M3 : Finition | Polissage et nettoyage final. |

**Contrainte d'Ordre :** Les messages doivent être lus et exécutés strictement dans l'ordre $1 \to 2 \to 3$.

---

## 3. 🐍 Indications pour le Producteur (Rôle : Garantie de l'Ordre d'Écriture)

Le producteur est le garant de l'ordre à la source.

### A. Configuration Essentielle

* **Identifiants :** Définir l'adresse du *broker* et le nom du *topic*.
* **Clé de Message (Cruciale) :** Définir une clé unique et constante pour le lot de travail (Ex. : `LOT_42`). Cette clé assure que tous les messages atterrissent dans la même partition.
* **Sérialisation :** Utiliser un sérialiseur comme JSON pour les valeurs et un sérialiseur simple pour la clé (ex: bytes).

### B. Paramètres de Fiabilité

Le producteur doit attendre une confirmation solide avant d'envoyer le message suivant :

1.  **Acquittement (`acks`) :** Configurer sur **`acks='all'`** (ou `-1`).
    * *Raison :* Garantit que le message est répliqué par tous les *In-Sync Replicas* (ISR), assurant une durabilité maximale et un ordre respecté même en cas de panne de la partition *leader*.
2.  **Idempotence :** Configurer **`enable_idempotence=True`**.
    * *Raison :* Préserve l'ordre et empêche les duplicata en cas de réessais réseau.

### C. Logique d'Envoi

1.  Parcourir la liste des ordres de travail (dans l'ordre $1 \to 2 \to 3$).
2.  Pour chaque ordre, appeler la méthode `producer.send()` en spécifiant **EXPLICITEMENT** la clé constante (`LOT_42`).
3.  Utiliser la méthode `future.get(timeout=...)` après chaque envoi pour s'assurer que l'écriture du message $M_n$ est confirmée par le *broker* avant de tenter l'envoi du message $M_{n+1}$.
    * *Raison :* C'est ce qui garantit que l'ordre $M_1 \to M_2 \to M_3$ sur le disque du *broker* correspond à l'ordre d'envoi du producteur.

---

## 4. 🐍 Indications pour le Consommateur (Rôle : Garantie de l'Ordre d'Exécution)

Le consommateur doit lire séquentiellement les messages de la partition et garantir que l'exécution de la machine est terminée avant de passer à l'étape suivante.

### A. Configuration Essentielle

* **Groupe de Consommateurs :** Définir un `group_id` unique.
* **Départ de Lecture :** Configurer `auto_offset_reset='earliest'` pour s'assurer de lire les ordres depuis le début (pour le test).

### B. Paramètres de Séquentialité (Cruciaux)

1.  **Commit Automatique :** Configurer **`enable_auto_commit=False`**.
    * *Raison :* Désactiver le commit automatique est la **clé de l'exécution séquentielle**. Le consommateur doit prendre lui-même la décision de marquer le message comme traité, uniquement après le succès.
2.  **Isolation :** (Optionnel mais recommandé pour la clarté) Configurer `max_poll_records=1` pour ne lire qu'un seul message à la fois lors de chaque *poll*.

### C. Logique de Traitement

1.  Démarrer la boucle de lecture (`for message in consumer:`).
2.  Pour chaque message reçu :
    a.  **Simuler le Travail :** Exécuter la fonction `process_order()` (simulant l'action de la machine-outil). Cette fonction doit inclure un `time.sleep()` pour simuler le temps d'exécution.
    b.  **Point de Contrôle (Commit Manuel) :** Après la *réussite* de l'opération `process_order()`, appeler **`consumer.commit()`** pour valider l'offset du message.
    * *Raison :* Si le processus s'arrête entre l'étape (a) et l'étape (b), le message n'est pas commité. Lorsque le consommateur redémarre, il reprendra la lecture à l'offset non commité, garantissant que l'opération non terminée sera rejouée avant de passer à l'étape suivante.

---

## 5. 🧑‍💻 Vérification de l'Ordre

Lancer le consommateur, puis lancer le producteur. Le résultat dans le terminal du consommateur doit toujours refléter l'ordre d'exécution :

1.  *Traitement pour Étape 1 (M1) commence...* $\to$ *Terminé* $\to$ *Commit*
2.  *Traitement pour Étape 2 (M2) commence...* $\to$ *Terminé* $\to$ *Commit*
3.  *Traitement pour Étape 3 (M3) commence...* $\to$ *Terminé* $\to$ *Commit*

