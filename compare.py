
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

cv = my_cv.cv

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


job1_desc = """

The Data Migration Specialist role is a multi-functional client facing role covering a variety of analytical and implementational tasks within the solutions department. You will be the point of contact between the company and the NHS, deliver and manage all aspects of data migration projects and provide support to other project members when required. You will have experience across a variety of healthcare systems and experience in a client facing role.

To be considered for this exciting opportunity, the successful Data Migration Specialist will require experience of;

    3-4 years of back-end healthcare systems experience.
    Experience should ideally cover: Cerner Millennium, Epic, Silverlink PCS, DXC Platform, System C Medway.
    Advanced SQL Data experience.
    Strong MS Office Skills – Excel, Word, Powerpoint.
    Good understanding of NHS Data Model
    Work collaboratively with the team, support project members where necessary.
    Good experience dealing with clients in a consultative way.

"""

file2_docs = sent_tokenize(job1_desc)

job_docs = [[w.lower() for w in word_tokenize(text)if w not in stopwords.words('english')if w.isalpha()]for text in file2_docs]

#query_doc = [word_tokenize(w) for w in job1_tokens]
query_doc_bow = [dictionary.doc2bow(doc) for doc in job_docs]

query_doc_tf_idf = tfidf[query_doc_bow]

sum_of_sims =(np.sum(sims[query_doc_tf_idf], dtype=np.float32))

percentage_of_similarity = round(float((sum_of_sims / len(cv_docs)) * 100))
print(f'Average similarity float: {float(sum_of_sims / len(cv_docs))}')
print(f'Average similarity percentage: {float(sum_of_sims / len(cv_docs)) * 100}')
print(f'Average similarity rounded percentage: {percentage_of_similarity}')


#jobs = pd.read_csv('data/jobs.csv')


#job_tokens =[]
#for i in jobs['desc']:
#    job_tokens.append([w for w in tokenizer.tokenize(i.lower()) if w not in stopwords.words('english')])


