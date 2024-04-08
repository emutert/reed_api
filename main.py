import requests as rq
from requests.auth import HTTPBasicAuth
import pandas as pd
import key
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self, api_key, base_url):
        self.auth = HTTPBasicAuth(api_key, "")
        self.session = rq.Session()
        self.session.auth = self.auth
        self.base_url = base_url
        self.df = pd.DataFrame()

    def get_data(self, start_range=0, end_range=1, step=1):
        data = []
        for i in range(start_range, end_range, step):
            try:
                response = self.session.get(self.base_url + str(i))
                response.raise_for_status()  # Raises stored HTTPError, if one occurred
                data += response.json()["results"]
            except rq.exceptions.HTTPError as errh:
                print(f"HTTP Error: {errh}")
            except rq.exceptions.ConnectionError as errc:
                print(f"Error Connecting: {errc}")
            except rq.exceptions.Timeout as errt:
                print(f"Timeout Error: {errt}")
            except rq.exceptions.RequestException as err:
                print(f"Something went wrong: {err}")
        self.df = self.df.from_dict(data)

    def extract_descriptions(self):
        descriptions = []
        for i in self.df["jobUrl"]:
            try:
                desc = ""
                for text in BeautifulSoup(rq.get(i).text, 'html.parser').findAll('span', attrs={"itemprop": "description"}):
                    desc += " " + text.text
                descriptions.append(desc)
            except Exception as e:
                print(f"Error in extracting job description: {e}")
        self.df["desc"] = descriptions

    def export_jobs(self, file_path):
        try:
            self.df[["jobUrl", "jobDescription", "desc"]].to_csv(file_path)
        except Exception as e:
            print(f"Error in exporting jobs: {e}")