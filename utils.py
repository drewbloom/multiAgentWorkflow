import faiss
import sqlite3
import numpy as np
import logging
import os
from dotenv import load_dotenv
import json
import PyPDF2

# Configure logging
logging.basicConfig(filename='multiAgent_Log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

class VectorStore:
    def __init__(self):
        self.dimension = 768  # Example vector dimension, adjust as needed
        self.index = faiss.IndexFlatL2(self.dimension)

    def add_vectors(self, vectors):
        """Add vectors to the index."""
        self.index.add(np.array(vectors))

    def search_vectors(self, query_vector, k=5):
        """Search for the top k vectors closest to the query vector."""
        distances, indices = self.index.search(np.array([query_vector]), k)
        return indices, distances

class SQLQuery:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Connect to the database when the context manager is entered
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection when the context manager is exited
        if self.conn:
            self.conn.close()

    def get_db_structure(self):
        # Get a list of all table names
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in self.cursor.fetchall()]

        # Get the schema for each table
        schemas = {}
        for table in tables:
            self.cursor.execute(f"PRAGMA table_info({table});")
            schemas[table] = self.cursor.fetchall()

        # Get a list of all indexes
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in self.cursor.fetchall()]

        # Get foreign keys
        foreign_keys = {}
        for table in tables:
            self.cursor.execute(f"PRAGMA foreign_key_list({table});")
            foreign_keys[table] = self.cursor.fetchall()

        return {
            "tables": tables,
            "schemas": schemas,
            "indexes": indexes,
            "foreign_keys": foreign_keys
        }

    def get_triggers(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
        triggers = [row[0] for row in self.cursor.fetchall()]
        return triggers

    def get_views(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = [row[0] for row in self.cursor.fetchall()]
        return views

    def enable_foreign_keys(self):
        self.cursor.execute("PRAGMA foreign_keys = ON;")

def load_api_key():
    return os.getenv('OPENAI_API_KEY')

def log_action(action_desc):
    # Log the action performed by an agent
    logging.info(action_desc)

def check_user_role(user_role):
    # Placeholder for role checking logic
    pass

# Call this method in the terminal and it runs the rest of the script - good for returning unicode-formatted full-text from the JSON conversion later in script
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text

def convert_to_json(metadata_dict):
    return json.dumps(metadata_dict, indent=4)

# Keep rest of code from running automatically when imported with if name = main block
if __name__ == "__main__":

    # Example Usage
    pdf_file_path = 'C:/Users/Drew/Desktop/Legal-Docs/Basic-Non-Disclosure-Agreement.pdf'
    full_text = extract_text_from_pdf(pdf_file_path)

    # instead of printing to console, let's print into the JSON object full-text field and ask user which area to enter it into within the JSON object (return a list)
    print(full_text)





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