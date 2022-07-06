import requests as rq
from requests.auth import HTTPBasicAuth
import pandas as pd
import key
from bs4 import BeautifulSoup

auth = HTTPBasicAuth(key.api_key, "")
session = rq.Session()
session.auth = auth

df = pd.DataFrame()
data = []
for i in range(0, 1000, 100):

    response = session.get(
        "https://www.reed.co.uk/api/1.0/search?keywords=Application%20Support&locationName=London&resultsToSkip="
        + str(i)
    )
    data += response.json()["results"]

df = df.from_dict(data)

#df[["jobUrl", "jobDescription"]].to_csv(r"data/jobs.csv")


for i in df["jobUrl"]:
    desc = ""
    for text in BeautifulSoup(rq.get(i).text,'html.parser').findAll('span', attrs={"itemprop":"description"}):
        desc += " " + text.text
    df["desc"] = desc


df[["jobUrl", "jobDescription","desc"]].to_csv(r"data/jobs.csv")
