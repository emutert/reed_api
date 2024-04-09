
from nltk.data import find
from nltk import download
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from gensim.corpora.dictionary import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import Similarity
from bs4 import BeautifulSoup
import requests
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
        # count the number of job's site 
        job_cnt = 0
        for url in jobs['jobUrl']:
            try:
                job_cnt += 1
                # get the job description
                response = requests.get(url)
                if response.status_code == 200:
                    # parse the job description
                    soup = BeautifulSoup(response.content, 'html.parser')
                    description = ""
                    # extract the job description
                    for el in soup.find_all("span", itemprop="description"):
                        description +=  str(el.get_text())
                    # Add the description to the dataframe
                    jobs.loc[jobs['jobUrl'] == url, 'fullDescription'] = description
                    # find the ASP value and add it to the dataframe
                    jobs.loc[jobs['jobUrl'] == url, 'asp'] = self.compare_job(dictionary, tfidf, corpus,description)
                else:
                    print(f"Error accessing URL: {url}")
                # sleep for 0.5 second after each 50th job
                if job_cnt == 50:
                    job_cnt = 0
                    time.sleep(0.5)                        
            except Exception as e:
                print(f"Error processing URL: {url} - {e}")
 
        # asp is more than 35%        
        return jobs[jobs.asp >=35]
    def compare_job(self,dictionary, tfidf, corpus, job_description):
        
        try:
            
            if dictionary and tfidf and corpus:
                sims = Similarity('data/', tfidf[corpus], num_features=len(dictionary))

                # CV and Job Description Comparison 
                # Tokenize and remove stop words
                file2_docs = sent_tokenize(job_description)
                # Tokenize and remove stop words
                job_docs = [[w.lower() for w in word_tokenize(text) if w not in stopwords.words('english') if w.isalpha()] for text in file2_docs]
                # Convert to bag-of-words
                query_doc_bow = [dictionary.doc2bow(doc) for doc in job_docs]
                # Convert to TF-IDF
                query_doc_tf_idf = tfidf[query_doc_bow]
                # Compute similarity
                sum_of_sims = np.sum(sims[query_doc_tf_idf], dtype=np.float32)
                
                # Return similarity percentage
                return float(sum_of_sims / len(corpus)) * 100
            else:
                return 0
        except Exception as e:
            print(f"An error occurred during job comparison: {e}")
            return 0
