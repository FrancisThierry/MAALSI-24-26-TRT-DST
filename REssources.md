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