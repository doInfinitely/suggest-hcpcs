from doltpy.core import Dolt
from doltpy.core.read import read_table
from levenshtein_distance import levenshtein_distance
from tf_idf import computeTFIDF, computeCosineSimilarity
import re

repo = Dolt('hospital-transparency-data')
df = read_table(repo, 'cpt_hcpcs')

desc = "Obstetric blood test".lower()

dist = []
for i in range(df.shape[0]):
    temp = df.loc[i]["long_description"].lower()
    dist.append((levenshtein_distance(desc, temp), df.loc[i]["code"]))
print("Suggesting top five codes by Levenshtein Distance:")
print(sorted(dist)[:5])


desc = re.sub(',;.', '', desc).split()
bagOfWords = dict()
for i in range(df.shape[0]):
    bagOfWords[df.loc[i]["code"]] = re.sub(',;.', '', df.loc[i]["long_description"]).lower().split()
print("Computing TF-IDF")
tfidf, termCounts, docCounts = computeTFIDF(bagOfWords)
print("Computing Cosine Similarity")
similarity = computeCosineSimilarity(desc, tfidf, docCounts)
print("Suggesting top five codes by TF-IDF Cosine Similarity:")
print(sorted([(similarity[key], key) for key in similarity], reverse=True)[:5])
