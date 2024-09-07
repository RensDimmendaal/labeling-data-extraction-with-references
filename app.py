from fasthtml.common import *
import os
import json
from pydantic import BaseModel, Field
from typing import List
from rich import print

# Data models
class Fact(BaseModel):
    fact: str = Field(...)
    substring_quote: str = Field(...)

class DataExtraction(BaseModel):
    job_title: Fact = Field(...)
    company: Fact = Field(...)
    location: Fact = Field(...)
    salary: Fact = Field(...)
    minimum_education: Fact = Field(...)

# Create the FastHTML app
app, rt = fast_app()

# Helper function to highlight the selected substring
def highlight_text(text: str, highlight: str):
    # Simple logic to wrap highlight text in <mark>
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

    field_forms = []
    for field_name, field_label in [("job_title", "Job Title"), ("company", "Company"), 
                                    ("location", "Location"), ("salary", "Salary"), 
                                    ("minimum_education", "Minimum Education")]:
        
        field_data = getattr(extraction, field_name)
        
        # Add the 'active-field' class if this is the active field
        form_class = "field-form"
        if field_name == active_field:
            form_class += " active-field"

        form = Form(
            Div(
                Label(field_label),
                Input(name="fact", value=field_data.fact, id=f"value-{field_name}"),
            ),
            Div(
                Label(f"{field_label} Substring Quotes"),
                Textarea(name="substring_quote", rows=3)(field_data.substring_quote),
            ),
            Button("Save", type="submit"),
            id=f"field-{field_name}-form",
            cls=form_class, # for styling
            action=f"/label/{filename}/{active_field}",
            method="post"
        )
        field_forms.append(form)

    return Grid(
            Div(*field_forms, cls="field-forms"),  # Left: forms for each field
            Div(
                H3("Job Posting Text"), 
                Pre(NotStr(highlighted_text), cls="job-posting"),
                cls="job-text-container"
            ), 
            columns=2
        )

# Route to save updated labels
@rt("/label/{filename}/{active_field}")
def post(filename: str, active_field: str, fact: Fact):
    # Load the existing label data
    label_path = f'extracted_labels/{filename}.json'
    with open(label_path, 'r') as f:
        label_data = json.load(f)

    # Update the fact and substring quotes for the active field
    label_data[active_field]['fact'] = fact.fact
    label_data[active_field]['substring_quote'] = fact.substring_quote

    # Save the updated data back to the json file
    with open(label_path, 'w') as f:
        json.dump(label_data, f, indent=4)
    
    # TODO: if we get here now we want to not reutrn the whole file but only update the current part of the form and then activate the next aprt of the form
    return RedirectResponse(f"/label/{filename}/{active_field}", status_code=303)

@rt("/static/{filename}")
def get_static(filename: str):
    return FileResponse(f'static/{filename}')


serve()
