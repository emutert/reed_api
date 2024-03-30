import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from bs4 import BeautifulSoup
import time
import logging

# API authentication (replace with your actual API key)
API_KEY = "your_api_key_here"
BASE_URL = "https://www.reed.co.uk/api/1.0/search"

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scrape_job_descriptions(keywords="Application Support", location="London", max_results=1000):
    """
    Scrapes job descriptions from Reed API and saves them to a CSV file.
    Args:
        keywords (str): Keywords for job search (default: "Application Support").
        location (str): Location for job search (default: "London").
        max_results (int): Maximum number of job descriptions to retrieve (default: 1000).
    """
    auth = HTTPBasicAuth(API_KEY, "")
    session = requests.Session()
    session.auth = auth

    df = pd.DataFrame()
    data = []

    for i in range(0, max_results, 100):
        try:
            response = session.get(f"{BASE_URL}?keywords={keywords}&locationName={location}&resultsToSkip={i}")
            response.raise_for_status()  # Raise an exception if the response status code is not 200
            data += response.json()["results"]
            logging.info(f"Retrieved {len(data)} job results")
            time.sleep(1)  # Throttle requests (1-second delay)
        except requests.RequestException as e:
            logging.error(f"Error fetching results: {e}")

    df = df.from_dict(data)

    descriptions = []
    for i, job_url in enumerate(df["jobUrl"]):
        try:
            soup = BeautifulSoup(requests.get(job_url).text, "html.parser")
            desc = " ".join(span.text for span in soup.find_all("span", attrs={"itemprop": "description"}))
            descriptions.append(desc)
            logging.info(f"Scraped description for job {i + 1}/{len(df)}")
        except Exception as e:
            logging.error(f"Error scraping job {i + 1}: {e}")
            descriptions.append("")  # Placeholder for failed scrapes

    df["desc"] = descriptions
    df[["jobUrl", "jobDescription", "desc"]].to_csv("data/jobs.csv", index=False)
    logging.info("Job descriptions saved to jobs.csv")

if __name__ == "__main__":
    scrape_job_descriptions(keywords="Software Engineer", location="Manchester", max_results=500)
