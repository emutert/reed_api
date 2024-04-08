
from nltk.data import find
from nltk import download
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from gensim.corpora.dictionary import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import Similarity
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time

class TextComparator:
    def __init__(self, cv, dictionary=None, tfidf=None, corpus=None,job_description=None):
        self.cv = cv
        self.dictionary = dictionary
        self.tfidf = tfidf
        self.corpus = corpus
        self.jobs = job_description

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
        
    def extract_descriptions_from_job_urls(self,jobs):
        # CV processing
        dictionary, tfidf, corpus = self.process_text()
        jobs['fullDescription'] = ''
        cnt = 0
        for url in jobs['jobUrl']:
            try:
                while cnt < 50: 
                    cnt += 1
                    response = requests.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        description = ""
                        for el in soup.find_all("span", itemprop="description"):
                            description +=  str(el.get_text())
                        # Add the description to the dataframe
                        jobs.loc[jobs['jobUrl'] == url, 'fullDescription'] = description
                        # find the ASP value and add it to the dataframe
                        jobs.loc[jobs['jobUrl'] == url, 'asp'] = self.compare_job(dictionary, tfidf, corpus,description)
                    else:
                        print(f"Error accessing URL: {url}")
                        
                else:
                    cnt = 0
                    time.sleep(2.5)
                        
            except Exception as e:
                print(f"Error processing URL: {url} - {e}")
 
        #jobs['fullDescription']= descriptions        
        return jobs
    def compare_job(self,dictionary, tfidf, corpus, job_description):
        try:
            
            if dictionary and tfidf and corpus:
                sims = Similarity('data/', tfidf[corpus], num_features=len(dictionary))

                # CV and Job Description Comparison 
                file2_docs = sent_tokenize(job_description)
                job_docs = [[w.lower() for w in word_tokenize(text) if w not in stopwords.words('english') if w.isalpha()] for text in file2_docs]
                query_doc_bow = [dictionary.doc2bow(doc) for doc in job_docs]
                query_doc_tf_idf = tfidf[query_doc_bow]
                sum_of_sims = np.sum(sims[query_doc_tf_idf], dtype=np.float32)
                #job_asp.append(float(sum_of_sims / len(corpus)) * 100)
                #jobs['asp']=pd.to_numeric(job_asp)
                # asp is more than 5%
                #return jobs[jobs.asp >=50]
                return float(sum_of_sims / len(corpus)) * 100
            else:
                return 0
        except Exception as e:
            print(f"An error occurred during job comparison: {e}")
            return 0
