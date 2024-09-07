from fasthtml.common import *
import os
import json
from pydantic import BaseModel, Field
from typing import List

# Data models
class Fact(BaseModel):
    fact: str = Field(...)
    substring_quote: List[str] = Field(...)

class DataExtraction(BaseModel):
    job_title: Fact = Field(...)
    company: Fact = Field(...)
    location: Fact = Field(...)
    salary: Fact = Field(...)
    minimum_education: Fact = Field(...)

# Create the FastHTML app
app, rt = fast_app()

# Route to display a list of available job postings for labeling
@rt("/")
def get():
    postings = os.listdir('postings')
    posting_links = [A(p, href=f"/label/{p.replace('.txt', '')}") for p in postings]
    return Titled("Labeling Tool", Div(*posting_links))

# Route to load the labeling interface
@rt("/label/{filename}")
def get(filename: str):
    # Load job posting text
    posting_path = f'postings/{filename}.txt'
    with open(posting_path, 'r') as f:
        posting_text = f.read()
    
    # Load corresponding labels (json)
    label_path = f'extracted_labels/{filename}.json'
    with open(label_path, 'r') as f:
        label_data = json.load(f)

    # Convert label_data to DataExtraction model
    extraction = DataExtraction(**label_data)

    # Create the form on the left with extracted labels
    form_elements = [
        Div(
            Label("Job Title"), 
            Input(name="job_title_fact", value=extraction.job_title.fact),
            Textarea(name="job_title_substring_quote", rows=2)(*extraction.job_title.substring_quote)
        ),
        Div(
            Label("Company"), 
            Input(name="company_fact", value=extraction.company.fact),
            Textarea(name="company_substring_quote", rows=2)(*extraction.company.substring_quote)
        ),
        Div(
            Label("Location"), 
            Input(name="location_fact", value=extraction.location.fact),
            Textarea(name="location_substring_quote", rows=2)(*extraction.location.substring_quote)
        ),
        Div(
            Label("Salary"), 
            Input(name="salary_fact", value=extraction.salary.fact),
            Textarea(name="salary_substring_quote", rows=2)(*extraction.salary.substring_quote)
        ),
        Div(
            Label("Minimum Education"), 
            Input(name="minimum_education_fact", value=extraction.minimum_education.fact),
            Textarea(name="minimum_education_substring_quote", rows=2)(*extraction.minimum_education.substring_quote)
        ),
        Button("Save", type="submit")
    ]
    
    # Create the form and the job posting text side by side
    form = Form(*form_elements, method="post", action=f"/save/{filename}")
    return Titled("Labeling Interface", Grid(form, Div(H3("Job Posting Text"), Pre(posting_text), cls="job-posting"), columns=2))

# Route to save updated labels
@rt("/save/{filename}")
def post(filename: str, job_title_fact: str, job_title_substring_quote: str, company_fact: str, company_substring_quote: str, location_fact: str, location_substring_quote: str, salary_fact: str, salary_substring_quote: str, minimum_education_fact: str, minimum_education_substring_quote: str):
    # Rebuild the data structure with the updated values
    updated_data = {
        "job_title": {
            "fact": job_title_fact,
            "substring_quote": job_title_substring_quote.splitlines()
        },
        "company": {
            "fact": company_fact,
            "substring_quote": company_substring_quote.splitlines()
        },
        "location": {
            "fact": location_fact,
            "substring_quote": location_substring_quote.splitlines()
        },
        "salary": {
            "fact": salary_fact,
            "substring_quote": salary_substring_quote.splitlines()
        },
        "minimum_education": {
            "fact": minimum_education_fact,
            "substring_quote": minimum_education_substring_quote.splitlines()
        }
    }
    
    # Save the updated labels to the json file
    label_path = f'extracted_labels/{filename}.json'
    with open(label_path, 'w') as f:
        json.dump(updated_data, f, indent=4)

    return RedirectResponse(f"/label/{filename}", status_code=303)

serve()
