# app.py
from flask import Flask, request, render_template
from main import JobScraper  # Import your function from the script
import key

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        job_name = request.form.get('job_name')  # Get the base_url from the form
        # Call your function with the base_url
        scraper = JobScraper(key.api_key, "https://www.reed.co.uk/api/1.0/search?keywords="+ job_name +"&locationName=London&resultsToSkip=")
        #scraper = JobScraper(key.api_key, "https://www.reed.co.uk/api/1.0/search?keywords=Application%20Support&locationName=London&resultsToSkip=")
        scraper.get_data()
        scraper.extract_descriptions()
        scraper.export_jobs(r"data/"+job_name+".csv")
        return "jobs.csv has been created."
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)