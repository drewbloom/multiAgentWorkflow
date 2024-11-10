import PyPDF2
import json

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text

# Example Usage
pdf_file_path = 'path/to/your/document.pdf'
full_text = extract_text_from_pdf(pdf_file_path)

# instead of printing to console, let's print into the JSON object full-text field and ask user which area to enter it into within the JSON object (return a list)
print(full_text)



def convert_to_json(metadata_dict):
    return json.dumps(metadata_dict, indent=4)

# Example Metadata
example_metadata = {
    "client": "Gonzalez",
    "matter": "Litigation",
    "abbreviation": "MOT",
    "description": "A motion to dismiss the case",
    "court_name": "Supreme Court",
    "court_location": "New York",
    "judge": "Judge Judy",
    # more fields as needed
    "full_text": full_text  # obtained from PDF extraction
}

json_data = convert_to_json(example_metadata)
print(json_data)