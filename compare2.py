
from nltk.data import find
from nltk import download
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from gensim.corpora.dictionary import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import Similarity

import pandas as pd
import numpy as np

class TextComparator:
    def __init__(self, cv, jobs=None):
        self.cv = cv
        self.jobs = jobs

    def process_text(self):
 
        try:
            find('tokenizers/punkt')
        except LookupError:
            download('punkt')

        try:
            find('corpora/stopwords')
        except LookupError:
            download('stopwords')

        try:
            file_docs = sent_tokenize(self.cv)
            cv_docs = [[w.lower() for w in word_tokenize(text) if w not in stopwords.words('english') if w.isalpha()] for text in file_docs]
            dictionary = Dictionary(cv_docs)
            corpus = [dictionary.doc2bow(doc) for doc in cv_docs]
            tfidf = TfidfModel(corpus)
            return dictionary, tfidf, corpus
        except Exception as e:
            print(f"An error occurred during text processing: {e}")
            return None, None, None

    def compare_jobs(self, jobs):
        try:
            dictionary, tfidf, corpus = self.process_text()
            if dictionary and tfidf and corpus:
                sims = Similarity('data/', tfidf[corpus], num_features=len(dictionary))
                jobs['asp']=0
                job_asp =[]
                #check column names in jobs
                #print(jobs.columns)
                for desc in jobs['jobDescription']:
                    file2_docs = sent_tokenize(desc)
                    job_docs = [[w.lower() for w in word_tokenize(text) if w not in stopwords.words('english') if w.isalpha()] for text in file2_docs]
                    query_doc_bow = [dictionary.doc2bow(doc) for doc in job_docs]
                    query_doc_tf_idf = tfidf[query_doc_bow]
                    sum_of_sims = np.sum(sims[query_doc_tf_idf], dtype=np.float32)
                    job_asp.append(float(sum_of_sims / len(corpus)) * 100)
                
                jobs['asp']=pd.to_numeric(job_asp)
                # asp is more than 5%
                return jobs[jobs.asp >=5]
            else:
                return None
        except Exception as e:
            print(f"An error occurred during job comparison: {e}")
            return None
