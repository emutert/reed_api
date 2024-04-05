# app.py
from flask import Flask, request, render_template,redirect,url_for
from main import JobScraper  # Import your function from the script
from compare2 import TextComparator  # Import your function from the script
import key

import PyPDF2
import flask as jsonify
app = Flask(__name__)

cv_text = ''
data_dict = dict()

@app.route('/upload', methods=['POST'])
def upload_file():
    pdf_file = request.files['pdf_file']
    if pdf_file and pdf_file.filename.endswith('.pdf') and len(pdf_file.read()) <= 204800:  # Checking if it's a PDF and within 20KB
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        global cv_text
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            cv_text += page.extract_text()
            print(cv_text)
        # Create a pandas dataframe from the text or perform further processing

        return redirect(url_for('home'))
        
    else:
        return "Please upload a PDF file that is maximum 20KB in size" + redirect(url_for('home'))
    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        job_name = request.form.get('job_name')  # Get the base_url from the form
        # Call your function with the base_url
        scraper = JobScraper(key.api_key, "https://www.reed.co.uk/api/1.0/search?keywords="+ job_name +"&locationName=London&resultsToSkip=")
        scraper.get_data()
        
        # This is for extracting job description from website
        #scraper.extract_descriptions()
        #scraper.export_jobs(r"data/"+job_name+".csv")
        #return "jobs.csv has been created."

        if scraper.df is not None:
            jobs = scraper.df
        else : return "Error occurred during job scraping. Please check the input data."

        comparator = TextComparator(cv_text)
        job_similarity = comparator.compare_jobs(jobs)
        return job_similarity[['jobUrl', 'jobDescription', 'asp']].to_html()

    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)