import sqlite3
import json

def create_connection():
    """Create a database connection to a SQLite database."""
    conn = sqlite3.connect('../database/mock_law_documents.db')
    return conn

def create_table(cursor):
    # Set up Table using the following Database Schema:
    # 
    # Client is the customer to the lawfirm e.g. Gonzalez
    # Matter is the type of legal proceeding e.g. litigation
    # Abbreviation is the type of action taken by the document e.g. MOT (Motion)
    # Description is a short explanation of purpose e.g. A motion to dismiss the case
    """Set up the documents table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            client TEXT,
            matter TEXT,
            abbreviation TEXT,
            description TEXT,
            court_name TEXT,
            court_location TEXT,
            judge TEXT,
            plaintiff_names TEXT,
            defendant_names TEXT,
            attorney_names TEXT,
            document_type TEXT,
            document_family TEXT,
            date TEXT,
            full_text TEXT
        )
    ''')

def insert_document_from_json(cursor, json_data):
    """Insert a document into the database from JSON data."""
    data = json.loads(json_data)
    cursor.execute('''
        INSERT INTO documents (
            client, matter, abbreviation, description, court_name, court_location, 
            judge, plaintiff_names, defendant_names, attorney_names, document_type, 
            document_family, date, full_text
        ) VALUES (
            :client, :matter, :abbreviation, :description, :court_name, :court_location, 
            :judge, :plaintiff_names, :defendant_names, :attorney_names, :document_type,
            :document_family, :date, :full_text
        )
    ''', data)

def setup_database_from_json(json_file_path):
    conn = create_connection()
    cursor = conn.cursor()
    create_table(cursor)

    with open(json_file_path, 'r') as file:
        json_data = file.read()
        insert_document_from_json(cursor, json_data)

    conn.commit()
    conn.close()

# User input to enter the filename for the JSON source
# Ensure the json_file_path points to the JSON file you've created with the necessary data.
json_file_path = f'C:/Users/Drew/Documents/Python Code/Repos/Personal/affinityPractice/multiAgentWorkflow/database/{input("Enter the JSON source filename for database creation (must be in database folder):\n")}'

setup_database_from_json(json_file_path)


# Original implementation via main.py:
# if __name__ == '__main__':
#    setup_database()