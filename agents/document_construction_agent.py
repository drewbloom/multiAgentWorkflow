from openai import OpenAI
import sqlite3
from utils import SQLQuery, log_action, load_api_key

client = OpenAI()
client.api_key = load_api_key()

class DocumentConstructionAgent:
    def __init__(self):
        self.agent_id = 'document_construction_agent_id'
        self.system_prompt = (
            "You are a Document Construction Agent. Create a complete document from a template using provided interview data as placeholders."
        )
        self.few_shot_examples = [
            {
                "role": "user",
                "content": "Create document from template with data: {'court_name': 'Supreme Court', 'date_of_creation': '2023-01-01'}"
            },
            {
                "role": "assistant",
                "content": "Document constructed with given data: [Full text with placeholders filled]."
            }
        ]

    ### Begin adding dynamic database interpretation to the constructor agent:
    # 1. Allow it to scan the database to understand what's in it
    def get_database_info(self, token):
        # Assuming the token is used to get the db_path (for now, directly using it)
        db_path = f"./database/{token}"  # Assuming the token is the filename or part of it
        
        # Using the context manager to handle the connection and automatically close it
        with SQLQuery(db_path) as query:
            # Get the database structure
            database_structure = query.get_db_structure()
            # can add request to get triggers and views if necessary later

        return {
            "database_structure": database_structure,
            # Leaving other options out for now
            # "triggers": triggers,
            # "views": views
        }



    def _fetch_template(self, document_type):
        # Connect to the database and get the latest document of a certain type
        conn = sqlite3.connect('mock_law_documents.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM documents WHERE document_type=? ORDER BY date_of_creation DESC LIMIT 1
        ''', (document_type,))
        document = cursor.fetchone()
        conn.close()
        return document

    def interview_for_metadata(self, user_agent):
        # Program questions to gather metadata from the user via UserInteractionAgent
        questions = [
            "What is the court name?",
            "Where is the court located?",
            "Who are the plaintiffs?",
            "Who are the defendants?",
            "Who are the attorneys?",
            "What is the date of creation?"
        ]
        
        metadata = {}
        for question in questions:
            response = user_agent.handle_user_input(user_agent.handle_assistant_input(question))
            metadata[question] = response

        return metadata

    def construct_document(self, document_type, user_agent):
        template = self._fetch_template(document_type)
        if template is None:
            log_action(f"No template found for document_type: {document_type}")
            return "No template found for the specified document type."

        # Perform the interview to fill in the metadata
        metadata = self.interview_for_metadata(user_agent)

        # Replace placeholders in the full_text with fetched metadata
        full_text = template[-1]  # Assuming last field is full_text
        for key, value in metadata.items():
            full_text = full_text.replace(f"{{{key}}}", value)

        # Return updated document (could be saved to file or returned as plain text)
        return full_text

    def get_metadata_schema(self):
        # Returns a JSON schema for document metadata fields
        return {
            "court_name": None,
            "court_location": None,
            "plaintiffs": None,
            "defendants": None,
            "attorneys": None,
            "date_of_creation": None
        }
    
    # Proposed usage of a JSON object return for metadata, not tested
    """
    def construct_document_with_ai(self, metadata):
        # Use AI to populate a template with the filled metadata
        filled_document = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Create document from template with data: {metadata}"}
            ]
        )

        result = filled_document.choices[0].message['content']
        log_action(f"Constructed document with AI: {result[:100]}...")
        return result
    """


    def construct_document_with_ai(self, document_type, user_agent):
        template = self._fetch_template(document_type)
        if template is None:
            return "No template found for the specified document type."
        
        full_text = template[-1]  # Assuming last field is full_text

        # Perform the interview to fill in the metadata
        metadata = self.interview_for_metadata(user_agent)

        # Using AI to generate document based on filled fields
        filled_document = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.few_shot_examples,
                {"role": "user", "content": f"Create document from template with data: {metadata}"}
            ]
        )

        # Returning generated document content
        result = filled_document.choices[0].message.content
        log_action(f"Constructed document with AI: {result[:100]}...")
        return result

    def construct_document_with_chunking(self, document_type, metadata):
        # Chunking logic - not yet used in the main function
        template = self._fetch_template(document_type)
        if template is None:
            return "No template found for the specified document type."

        full_text = template[-1]
        chunks = self.chunk_text(full_text)
        completed_document = ""

        for chunk in chunks:
            filled_chunk = OpenAI().chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Fill placeholders with provided metadata where appropriate"},
                    {"role": "user", "content": f"Fill chunk with data if data belongs in open fields.  If you don't think an open field has a match in the provided data, leave it blank for a return to the user later. Data: {metadata}. Chunk: {chunk}"}
                ]
            )
            completed_document += filled_chunk.choices[0].message.content

        log_action(f"Constructed document with chunking: {completed_document[:100]}...")
        return completed_document

    def chunk_text(self, text, chunk_size=1024):
        # Basic chunking function to split text for processing in parts
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]