
## 🛠️ TD : Le Processor (Consumer-Producer) Kafka sans Code

### 🎯 Objectif du TD

Construire une application Python hybride (un **Processor**) qui consomme des données brutes d'un topic, effectue une transformation numérique (calcul), puis publie le résultat dans un second topic.

---

### 📚 Étape 1 : Préparation et Jeu de Données

#### 1.1 Préparation des Topics
Utilisez les outils d'administration de Kafka (CLI ou interface web) pour créer les deux topics nécessaires :

1.  **Topic Source (INPUT) :** `temperatures_celsius_raw`
    * *Paramètres recommandés :* 3 partitions, facteur de réplication 1.
2.  **Topic Destination (OUTPUT) :** `temperatures_fahrenheit_processed`
    * *Paramètres recommandés :* 3 partitions, facteur de réplication 1.

#### 1.2 Jeu de Données Source
Les données brutes qui seront envoyées au topic `temperatures_celsius_raw` doivent être au format **JSON**, structurées comme suit :

| Clé (Key) | Valeur (Value - JSON String) | Description |
| :--- | :--- | :--- |
| `sensor_id` (Ex: `SENS_A`) | `{"id": 1, "location": "NYC", "celsius": 10.5}` | Température brute en Celsius. |
| `sensor_id` (Ex: `SENS_B`) | `{"id": 2, "location": "PAR", "celsius": 20.0}` | Température brute en Celsius. |
| `sensor_id` (Ex: `SENS_A`) | `{"id": 3, "location": "NYC", "celsius": 12.2}` | Nouvelle valeur pour le même capteur. |

### 🔨 Étape 2 : Le Producteur de Test (Input)

**Instruction :** Créez le script Python `producer_input.py`.

1.  **Instanciation :** Créez une instance de `KafkaProducer`.
2.  **Sérialisation/Encodage :** Assurez-vous que les données JSON (valeur) sont sérialisées en chaînes de caractères puis encodées en *bytes* (UTF-8) avant l'envoi. La clé (qui est la chaîne `sensor_id`) doit également être encodée en *bytes*.
3.  **Flux d'Envoi :** Envoyez les trois messages du tableau ci-dessus (dans cet ordre) au topic **`temperatures_celsius_raw`**.
4.  **Confirmation :** Implémentez un *callback* pour confirmer la livraison des messages et afficher la partition et l'offset.

---

### ⚙️ Étape 3 : Le Processor (Consumer-Producer)

**Instruction :** Créez le script Python `processor_app.py`. C'est le cœur du TD.

#### 3.1 Configuration des Clients
1.  **Consommateur (Input) :** Instanciez un `KafkaConsumer` abonné au topic **`temperatures_celsius_raw`**.
    * *Configuration :* Définissez un `group_id` unique (ex: `temp_converter_group`).
2.  **Producteur (Output) :** Instanciez un `KafkaProducer` pour envoyer au topic **`temperatures_fahrenheit_processed`**.

#### 3.2 Implémentation de la Logique de Transformation
Dans la boucle principale de lecture du Consommateur, effectuez les actions suivantes :

1.  **Désérialisation :** Récupérez la valeur du message et désérialisez-la (décodez les *bytes* en chaîne de caractères, puis parsez la chaîne en objet Python/dictionnaire).
2.  **Transformation :** Appliquez la formule de conversion à la valeur du champ `celsius`.
    $$F = C \times 1.8 + 32$$
3.  **Construction du Message Sortant :** Créez un nouveau dictionnaire (objet Python) pour le message de sortie. Ce message doit inclure :
    * La clé `sensor_id` (récupérée du message entrant).
    * Le champ `location` original.
    * Le nouveau champ `fahrenheit` (avec le résultat du calcul).
    * Un champ de traçabilité, par exemple `source_topic` ou `processed_timestamp`.
4.  **Sérialisation/Envoi :** Sérialisez ce nouvel objet en JSON, encodez-le en *bytes*, et envoyez-le au topic **`temperatures_fahrenheit_processed`**, en utilisant la même clé (`sensor_id`).


#### 3.3 Gestion des Erreurs
1.  Implémentez un bloc `try...except` autour de l'étape de désérialisation pour gérer les messages mal formés (qui ne sont pas du JSON valide) sans arrêter le Processor.

---

### ✅ Étape 4 : Le Consommateur de Validation (Output)

**Instruction :** Créez le script Python `consumer_output.py`.

1.  **Instanciation :** Créez un `KafkaConsumer` abonné au topic **`temperatures_fahrenheit_processed`**.
2.  **Validation :** Lancez ce Consommateur en dernier. Il doit afficher les messages reçus.
3.  **Vérification :** Confirmez que chaque message contient la température convertie en Fahrenheit et que les valeurs sont cohérentes avec le calcul.
