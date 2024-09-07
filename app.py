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

# Helper function to highlight the selected substring
def highlight_text(text: str, highlights: List[str]):
    # Simple logic to wrap highlight text in <mark>
    for highlight in highlights:
        if highlight in text:
            text = text.replace(highlight, f"<mark>{highlight}</mark>")
    return text

# Route to display a list of available job postings for labeling
@rt("/")
def get():
    postings = os.listdir('postings')
    posting_links = [A(p, href=f"/label/{p.replace('.txt', '')}") for p in postings]
    return Titled("Labeling Tool", Div(*posting_links))

@rt("/label/{filename}/")
def get(filename: str):
    # TODO make variable...now it's hardcoded to job_title
    return RedirectResponse(url=f"/label/{filename}/job_title")

# Route to load the labeling interface with improved text highlighting
@rt("/label/{filename}/{active_field}")
def get(filename: str, active_field: str):
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

    # Get the currently active field and corresponding substring quotes
    active_fact = getattr(extraction, active_field)

    # Highlight the substring_quotes in the job posting text
    highlighted_text = highlight_text(posting_text, active_fact.substring_quote)

    # Form elements for each field
    fields = [
        ("job_title", "Job Title", extraction.job_title),
        ("company", "Company", extraction.company),
        ("location", "Location", extraction.location),
        ("salary", "Salary", extraction.salary),
        ("minimum_education", "Minimum Education", extraction.minimum_education)
    ]

    form_elements = []
    for field_name, label, fact in fields:
        cls = "active-field" if field_name == active_field else ""
        form_elements.append(
            Div(
                Label(label), 
                Input(name=f"{field_name}_fact", value=fact.fact),
                Textarea(name=f"{field_name}_substring_quote", rows=2)(*fact.substring_quote),
                Button(f"Edit {label}", onclick=f"window.location.href='/label/{filename}/{field_name}'"),
                cls=cls
            )
        )
    
    # Add a button for updating substring quote via text selection
    form_elements.append(Button("Update Selected Text", id="update-substring"))

    # Create the form and the job posting text with highlights
    form = Form(*form_elements, method="post", action=f"/save/{filename}/{active_field}")
    return Titled(
        "Labeling Interface",
        Grid(
            form, 
            Div(
                H3("Job Posting Text"), 
                Pre(NotStr(highlighted_text), cls="job-posting"),
                cls="job-text-container"
            ), 
            columns=2
        )
    )

# Route to save updated labels
@rt("/save/{filename}/{active_field}")
def post(filename: str, active_field: str, **form_data):
    # Load the existing label data
    label_path = f'extracted_labels/{filename}.json'
    with open(label_path, 'r') as f:
        label_data = json.load(f)

    # Update the fact and substring quotes for the active field
    label_data[active_field]['fact'] = form_data[f"{active_field}_fact"]
    label_data[active_field]['substring_quote'] = form_data[f"{active_field}_substring_quote"].splitlines()

    # Save the updated data back to the json file
    with open(label_path, 'w') as f:
        json.dump(label_data, f, indent=4)

    return RedirectResponse(f"/label/{filename}/{active_field}", status_code=303)

@rt("/static/{filename}")
def get_static(filename: str):
    return FileResponse(f'static/{filename}')


serve()
