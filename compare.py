
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

from gensim.corpora.dictionary import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import Similarity


import my_cv
import pandas as pd
import numpy as np
#cv will read from file
#file upload will be available

cv = my_cv.cv2

#sentence tokenization
file_docs = sent_tokenize(cv)

#preprocess
#tokenization, lowercase, remove punctuation and stops words
cv_docs = [[w.lower() for w in word_tokenize(text)if w not in stopwords.words('english')if w.isalpha()]for text in file_docs]

#documents to dictionary
dictionary = Dictionary(cv_docs)

#
corpus = [dictionary.doc2bow(doc) for doc in cv_docs]

tfidf = TfidfModel(corpus)

sims = Similarity('data/',tfidf[corpus],num_features=len(dictionary))

#CV / Collected job descs average similarity percantages 
#to-do: make this file free
jobs = pd.read_csv('data/jobs.csv')

job_asp =[]
for i in jobs['desc']:
    file2_docs = sent_tokenize(i)
    job_docs = [[w.lower() for w in word_tokenize(text)if w not in stopwords.words('english')if w.isalpha()]for text in file2_docs]
    query_doc_bow = [dictionary.doc2bow(doc) for doc in job_docs]

    query_doc_tf_idf = tfidf[query_doc_bow]

    sum_of_sims =(np.sum(sims[query_doc_tf_idf], dtype=np.float32))
    job_asp.append(float(sum_of_sims / len(cv_docs)) * 100)

jobs["asp"]=pd.to_numeric(job_asp)

jobs[jobs.asp >=35].to_csv(r'data/35andbigger.csv')

