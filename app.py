from fasthtml.common import *
import os
import json
from pydantic import BaseModel, Field
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


def next_field(base_model, current_field: str) -> str:
    fields = list(DataExtraction.model_json_schema().get("properties").keys())
    try:
        return fields[fields.index(current_field) + 1]
    except IndexError:
        raise NotImplementedError(
            "Haven't figured out what to do after labeling last field yet"
        )


markdown_js = """
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
import { proc_htmx} from "https://cdn.jsdelivr.net/gh/answerdotai/fasthtml-js/fasthtml.js";
proc_htmx('.markdown', e => e.innerHTML = marked.parse(e.textContent));
"""

# We will use this in our `exception_handlers` dict
def _not_found(req, exc): return Titled('Oh no!', Div('We could not find that page :('))
# The `FastHTML` class is a subclass of `Starlette`, so you can use any parameters that `Starlette` accepts.
# In addition, you can add your Beforeware here, and any headers you want included in HTML responses.
# FastHTML includes the "HTMX" and "Surreal" libraries in headers, unless you pass `default_hdrs=False`.
app = FastHTML(
               # These are the same as Starlette exception_handlers, except they also support `FT` results
               exception_handlers={404: _not_found},
               # PicoCSS is a particularly simple CSS framework, with some basic integration built in to FastHTML.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               # You can use any CSS framework you want, or none at all.
               hdrs=(picolink,
                       Link(rel='stylesheet', href='/static/styles.css', type='text/css'),
                    #    Style(".job-posting {color: red;}")
                     # `Style` is an `FT` object, which are 3-element lists consisting of:
                     # (tag_name, children_list, attrs_dict).
                     # FastHTML composes them from trees and auto-converts them to HTML when needed.
                     # You can also use plain HTML strings in handlers and headers,
                     # which will be auto-escaped, unless you use `NotStr(...string...)`.
                    #  Style(':root { --pico-font-size: 100%; }'),
                     # Have a look at fasthtml/js.py to see how these Javascript libraries are added to FastHTML.
                     # They are only 5-10 lines of code each, and you can add your own too.
                    #  SortableJS('.sortable'),
                     # MarkdownJS is actually provided as part of FastHTML, but we've included the js code here
                     # so that you can see how it works.
                    #  Script(markdown_js, type='module')
                     )
)

rt = app.route

# Helper function to highlight the selected substring
def highlight_text(text: str, highlight: str):
    # Simple logic to wrap highlight text in <mark>
    if highlight in text:
        text = text.replace(highlight, f"<mark>{highlight}</mark>")
    return text


def generate_forms(extraction, active_field, filename):
    """Helper function to generate all form sections"""
    field_forms = []
    for field_name, field_label in [
        ("job_title", "Job Title"),
        ("company", "Company"),
        ("location", "Location"),
        ("salary", "Salary"),
        ("minimum_education", "Minimum Education"),
    ]:

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
            cls=form_class,  # for styling
            action=f"/label/{filename}/{field_name}",
            method="post",
        )
        field_forms.append(form)

    return Div(
        *field_forms, cls="field-forms"
    )  # Return all forms wrapped in a div with a common class


# Route to display a list of available job postings for labeling
@rt("/")
def get():
    postings_dir = "./data/job_postings/inputs/"
    extracted_labels_dir = "./data/job_postings/predictions/"

    # Load all postings and their corresponding labels
    postings = []
    for filename in os.listdir(postings_dir):
        if filename.endswith(".txt"):
            posting_name = filename[:-4]
            posting_path = os.path.join(postings_dir, filename)
            label_path = os.path.join(extracted_labels_dir, f"{posting_name}.json")

            with open(posting_path, "r") as f:
                posting_text = f.read()

            with open(label_path, "r") as f:
                label_data = json.load(f)

            postings.append((posting_name, posting_text, label_data))

    # Generate the table
    table_headers = ["Posting Name"] + list(postings[0][2].keys())
    table_rows = []
    for posting_name, posting_text, label_data in postings:
        row = [A(posting_name, href=f"/label/{posting_name}/job_title")] + [label_data[field]['fact'] for field in table_headers[1:]]
        table_rows.append(row)

    return Titled(
        "Job Postings",
        Table(
            Tr(*[Th(header) for header in table_headers]),
            *[Tr(*[Td(cell) for cell in row]) for row in table_rows]
        ),
    )


@rt("/label/{filename}/")
def get(filename: str):
    # TODO make variable...now it's hardcoded to job_title
    return RedirectResponse(url=f"/label/{filename}/job_title")


# Route to load the labeling interface with improved text highlighting


@rt("/label/{filename}/{active_field}")
def get(filename: str, active_field: str):
    # Load job posting text
    posting_path = f"./data/job_postings/inputs/{filename}.txt"
    with open(posting_path, "r") as f:
        posting_text = f.read()

    # Load corresponding labels (json)
    label_path = f"./data/job_postings/predictions/{filename}.json"
    with open(label_path, "r") as f:
        label_data = json.load(f)

    # Convert label_data to DataExtraction model
    extraction = DataExtraction(**label_data)

    # Get the currently active field and corresponding substring quotes
    active_fact = getattr(extraction, active_field)

    # Highlight the substring_quotes in the job posting text
    highlighted_text = highlight_text(posting_text, active_fact.substring_quote)

    return Div(
        Grid(
            Div(
                H3("Extractions"),
                generate_forms(extraction, active_field, filename),
            ),
            Div(
                H3("Job Posting Text"),
                Div(NotStr(highlighted_text), cls="job-posting"),
                cls="job-text-container",
            ),
            columns=2,
        ),
        Script(src="/static/script.js"),
        cls="container",
    )


# Route to save updated labels
@rt("/label/{filename}/{active_field}")
def post(filename: str, active_field: str, fact: Fact):
    # Load the existing label data
    label_path = f"data/job_postings/human_labels/{filename}.json"
    with open(label_path, "r") as f:
        label_data = json.load(f)

    # Update the fact and substring quotes for the active field
    label_data[active_field]["fact"] = fact.fact
    label_data[active_field]["substring_quote"] = fact.substring_quote

    # Save the updated data back to the json file
    with open(label_path, "w") as f:
        json.dump(label_data, f, indent=4)

    return RedirectResponse(
        f"/label/{filename}/{next_field(DataExtraction, active_field)}", status_code=303
    )


@rt("/static/{filename}")
def get_static(filename: str):
    return FileResponse(f"static/{filename}")


serve(reload_includes=["static/*"])
