## Documentation Pyspark
https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html

## filtre sur année
df_title = spark.read.csv('./title.basics.tsv', header=True, sep="\t")

df_title = df_title.dropna()

df_cleaned = df_title.filter(df_title["endYear"].isNotNull())
df_cleaned = df_title.filter(df_title["endYear"] != "\\N")


df_cleaned = df_title.filter(
    (df_title["endYear"].isNotNull()) & (df_title["endYear"] != "\\N")
)



df_cleaned.sort("endYear",ascending=False).show(5)


## Estimation ressources

### La Formule de Base (Estimation RAM)

Pour un traitement confortable (éviter les déversements sur disque ou "spills" qui ralentissent tout), vous devez estimer la taille de vos données une fois décompressées en mémoire.

$$N_{machines} = \frac{T_{disque} \times F_{expansion} \times (1 + M_{sécurité})}{RAM_{par\_machine} \times T_{utilisable}}$$

**Les variables :**
* $T_{disque}$ : Taille de votre dataset sur le disque (ex: 500 Go).
* $F_{expansion}$ : Facteur de décompression/sérialisation (voir ci-dessous).
* $M_{sécurité}$ : Marge de manœuvre pour les pics de charge (généralement 20% à 50%, soit $0.2 - 0.5$).
* $RAM_{par\_machine}$ : RAM totale physique d'un nœud.
* $T_{utilisable}$ : Pourcentage de RAM allouée réellement à Spark (généralement 75% à 80% pour laisser de la place à l'OS).



### Étape 1 : Estimer le Facteur d'Expansion ($F_{expansion}$)
Les données sur disque (surtout Parquet/ORC/Avro) sont souvent très compressées. En mémoire (objets Java/Scala), elles prennent beaucoup plus de place.

* **Parquet / ORC (Snappy/Gzip) :** Comptez **2x à 4x**. (100 Go sur disque $\approx$ 300 Go en RAM).
* **CSV / JSON :** Comptez **1x à 1.5x** (le format texte est déjà verbeux, mais l'overhead des objets Java ajoute du poids).
* **Données complexes (Arrays/Maps imbriqués) :** Comptez **4x à 5x**.

### Étape 2 : Exemple Concret de Calcul

Imaginons le scénario suivant :
* **Dataset :** 1 To (1000 Go) de fichiers **Parquet**.
* **Machines disponibles :** Nœuds de 64 Go de RAM avec 16 Cœurs.
* **Charge de travail :** Jointures et agrégations standard (nécessite du "Shuffle").

**Le calcul :**

1.  **Taille en mémoire ($T_{disque} \times F_{expansion}$) :**
    $$1000 \text{ Go} \times 3 (\text{Moyenne Parquet}) = 3000 \text{ Go requis}$$

2.  **Marge de sécurité ($+ 25\%$) :**
    $$3000 \text{ Go} \times 1.25 = 3750 \text{ Go Total Cible}$$

3.  **RAM utilisable par machine :**
    Sur 64 Go, on laisse ~4 Go pour l'OS et les démons Hadoop/K8s.
    $$64 \text{ Go} - 4 \text{ Go} = 60 \text{ Go}$$
    Spark n'utilise pas 100% de la heap pour le stockage (voir `spark.memory.fraction`). Disons 60 Go utilisables pour simplifier.

4.  **Nombre de machines :**
    $$\frac{3750}{60} = 62.5$$

> **Résultat :** Il vous faudrait environ **63 machines** pour traiter ce dataset *entièrement en mémoire* pour une performance maximale.

---

### Nuance Importante : Batch vs Caching

Le calcul ci-dessus vise une performance optimale où presque tout tient en RAM (idéal pour l'analytique itérative ou le Machine Learning).

Cependant, pour un simple job **ETL Batch** (lecture $\rightarrow$ transformation $\rightarrow$ écriture) qui ne fait pas de `.cache()` ou `.persist()`, vous n'avez pas besoin de charger tout le dataset en même temps. Spark traite les données par partitions.

**Pour un job Batch standard (ETL), vous pouvez diviser le résultat par 2 ou 3 :**
* Dans l'exemple ci-dessus, **20 à 30 machines** suffiraient probablement, mais le job sera plus lent car il devra charger et décharger les partitions plus souvent.

### Vérification par les Cœurs (CPU)

Il faut aussi vérifier que vous avez assez de parallélisme.
* Règle : On vise généralement **2 à 4 tâches (tasks) par cœur CPU**.
* Spark divise les données en partitions (par défaut 128 Mo).
* Pour 1 To de données : $1 000 000 \text{ Mo} / 128 \text{ Mo} \approx 7800 \text{ partitions}$.
* Avec 30 machines à 16 cœurs = 480 cœurs totaux.
* $7800 / 480 = 16$ vagues de tâches. C'est un ratio très sain.
## Pour TD Kafka

```bash
pip install kafka-python

docker compose up 
```
Dans le répertoire TD Kafka
