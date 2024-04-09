import requests as rq
from requests.auth import HTTPBasicAuth
import pandas as pd
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self, api_key, base_url,job_url=None):
        self.auth = HTTPBasicAuth(api_key, "")
        self.session = rq.Session()
        self.session.auth = self.auth
        self.base_url = base_url
        self.df = pd.DataFrame()
        self.job_url = job_url

    def get_data(self, start_range=0, end_range=1, step=1):
        """
        This method sends a series of API requests to collect job data and store it in a pandas DataFrame

        :param start_range: starting index for the API requests (default=0)
        :param end_range: ending index for the API requests (default=1000)
        :param step: step size between API requests (default=100)
        :return: None
        """
        data = []
        for i in range(start_range, end_range, step):
            try:
                response = self.session.get(self.base_url + f"?resultsToSkip={i}&resultsPerPage={step}")
                response.raise_for_status()
                data += response.json()['results']
            except (rq.exceptions.HTTPError, rq.exceptions.ConnectionError,
                    rq.exceptions.Timeout, rq.exceptions.RequestException) as err:
                print(f"Error occurred during GET request: {err}")
        self.df = self.df.from_dict(data)

    def extract_descriptions(self, job_url):

        try:
            desc = ""
            for text in BeautifulSoup(rq.get(job_url).text, 'html.parser').findAll('span', attrs={"itemprop": "description"}):
                desc += " " + text.text
            return desc
        except Exception as e:
            print(f"Error in extracting job description: {e}")


    def export_jobs(self, file_path):
        try:
            self.df[["jobUrl", "jobDescription", "desc"]].to_csv(file_path)
        except Exception as e:
            print(f"Error in exporting jobs: {e}")