# app.py
from flask import Flask, request, render_template,redirect,url_for
from main import JobScraper, extract_descriptions  # Import your function from the script
from compare2 import TextComparator  # Import your function from the script
import key
import asyncio
import PyPDF2

app = Flask(__name__)

cv_text = ''
full_description = ''

async def process_job_similarity( cv_text, jobs):
    comparator = TextComparator(cv_text)
    tasks = []
    for url in jobs['jobUrl']:
        tasks.append(asyncio.create_task(asyncio.to_thread(extract_descriptions, jobs,url)))
        tasks.append(asyncio.create_task(asyncio.to_thread(comparator.calculate_asp, url,jobs)))
    await asyncio.gather(*tasks)
    #full_description = await asyncio.to_thread(extract_descriptions, url)
    #jobs.loc[jobs['jobUrl'] == url, 'fullDescription'] = full_description
    #await asyncio.to_thread(comparator.calculate_asp, url,jobs,full_description)
    job_similarity_result = jobs[['jobUrl', 'jobDescription', 'asp']][jobs.asp >= 35]
    return job_similarity_result

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    This function is triggered when the user submits the form in index.html with the method POST.
    The form has an input with the name 'pdf_file' which is a file input.
    The function checks if the file is a PDF file (ending with .pdf) and the file size is <= 20KB.
    If the conditions are met, the function extracts text from the PDF file and save it to the global variable cv_text.
    """
    pdf_file = request.files['pdf_file']
    # Check if the input file is a PDF file and the file size is <= 20KB
    if pdf_file and pdf_file.filename.endswith('.pdf') and len(pdf_file.read()) <= 204800:
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        global cv_text
        # Extract text from each page in the PDF file and save it to the global variable cv_text
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            cv_text += page.extract_text()
        # Close the stream of the PDF file
        pdf_file.close()
        # Redirect to the home route after the file is processed
        return redirect(url_for('home'))
    # If the conditions are not met, return an error message and redirect to the home route
    else:
        return "Please upload a PDF file that is maximum 20KB in size" + redirect(url_for('home'))

    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        job_name = request.form.get('job_name')  # Get the base_url from the form
        # establish the connection with the API
        scraper = JobScraper(key.api_key, "https://www.reed.co.uk/api/1.0/search?keywords="+ job_name +"&locationName=London&resultsToSkip=")
        # Call get_data with the base_url
        scraper.get_data()
        # Check if the get_data method returned a DataFrame
        if scraper.df is not None:
            jobs = scraper.df
            print("length of jobs is ",len(jobs))
        else : return "Error occurred during job scraping. Please check the input data." + redirect(url_for('home'))
        # Call TextComparator with the imported cv_text and base_url
        comparator = TextComparator(cv_text)
        # This is for extracting job description from website and compare with cv
        #job_similarity = comparator.extract_descriptions_from_job_urls(jobs)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        job_similarity_result=loop.run_until_complete(process_job_similarity(cv_text, jobs))
        '''for url in jobs['jobUrl']:
            try:
                #full_description = scraper.extract_descriptions(url)
                #jobs.loc[jobs['jobUrl'] == url, 'fullDescription'] = full_description
                # find the ASP value and add it to the dataframe
                #comparator.calculate_asp(url,jobs,full_description)
                job_similarity_result=loop.run_until_complete(process_job_similarity(cv_text, url, jobs))
            except Exception as e:
                print(f"Error processing URL: {url} - {e}") 
        '''
        # This is for extracting job description from website
        #scraper.extract_descriptions()
        #scraper.export_jobs(r"data/"+job_name+".csv")
        #return "jobs.csv has been created."
        #job_similarity[["jobUrl", "jobDescription", "asp"]].to_csv(r"data/"+job_name+".csv")
        #return "jobs.csv has been created."
        
        return render_template('job_similarity.html', job_similarity_result=job_similarity_result)

        
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)