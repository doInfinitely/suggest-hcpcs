import pandas as pd
#from sklearn.feature_extraction.text import TfidfVectorizer
#from nltk.corpus import stopwords
import math
#stopwords.words('english')

def computeTermCounts(bagOfWords):
    termCounts = dict()
    uniqueWords = set()
    for key in bagOfWords:
        uniqueWords |= set(bagOfWords[key])
    for key in bagOfWords:
        termCounts[key] = dict.fromkeys(uniqueWords, 0)
        for word in bagOfWords[key]:
            termCounts[key][word] += 1
    return termCounts

def computeDocCounts(termCounts):
    docCounts = dict()
    for key in termCounts:
        for word, val in termCounts[key].items():
            if val > 0:
                if word not in docCounts:
                    docCounts[word] = 0
                docCounts[word] += 1 
    return docCounts

def computeTFIDF(bagOfWords):
    termCounts = computeTermCounts(bagOfWords)
    docCounts = computeDocCounts(termCounts)
    tfidf = dict()
    N = len(docCounts)
    for key in termCounts:
        tfidf[key] = dict()
        for word, val in termCounts[key].items():
            tfidf[key][word] = val/len(bagOfWords[key]) * math.log(N/docCounts[word])
    return tfidf, termCounts, docCounts

def computeCosineSimilarity(bag, tfidf, docCounts):
    bagCounts = dict()
    for word in bag:
        if word not in bagCounts:
            bagCounts[word] = 0
        bagCounts[word] += 1
    embedding = dict()
    N = len(docCounts)
    norm = 0
    for key in bagCounts:
        if key in docCounts:
            embedding[key] = bagCounts[key]/len(bag) * math.log(N/docCounts[key])
            norm += embedding[key]**2
    for key in embedding:
        try:
            embedding[key] /= norm**0.5
        except ZeroDivisionError:
            pass

    similarity = dict()
    for key in tfidf:
        similarity[key] = 0
        norm = 0
        for word in tfidf[key]:
            if word in embedding:
                similarity[key] += embedding[word]*tfidf[key][word]
            norm += tfidf[key][word]**2
        similarity[key] /= norm**0.5
    return similarity

if __name__ == "__main__":
    documents = {
            'documentA':'the man went out for a walk',
            'documentB':'the children sat around the fire'}
    bagOfWords = {key:documents[key].split(' ') for key in documents}
    tfidf, termCounts, docCounts = computeTFIDF(bagOfWords)
    #print(tfidf)
    print(computeCosineSimilarity(bagOfWords['documentA'], tfidf, docCounts))
