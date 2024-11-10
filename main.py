from agents.user_interaction_agent import UserInteractionAgent
from agents.knowledge_search_agent import KnowledgeSearchAgent
from agents.document_construction_agent import DocumentConstructionAgent
from agents.qa_agent import QA_Agent

def main():
    user_agent = UserInteractionAgent()
    search_agent = KnowledgeSearchAgent()
    construction_agent = DocumentConstructionAgent()
    qa_agent = QA_Agent()

    user_input = input('Enter user message...')

    user_response = user_agent.handle_user_input(user_input)
    print(f"User Agent Response: {user_response}")

    if "search" in user_response:
        print("Searching your database for relevant documents...")
        search_results = search_agent.perform_search(user_input)

        print("Verifying search results for consistency...")
        quality_response = qa_agent.verify_output_with_ai(search_results)
        print("Final processed output:", quality_response)

    elif "construct" in user_response:
        print("Preparing an interview for document creation...")
        # Contact the construction agent
        document = construction_agent.construct_document_with_ai("NDA", user_agent=user_agent)
        
        print("Document completed:\n\n" + document)
        
        # AI suggested implementation - leaving out for now
        """
        # Get the user agent to send a JSON object to the document constructor
        metadata = {
            'court_name': "Example Court",
            'date_of_creation': "2023-01-01"
            # Assume further metadata as needed
        }
        print("Creating a final document based on your interview responses...")
        # Current implementation - single-shot of full doc creation (also have a chunked implementation to test; will require more few shots to work correctly)
        constructed_doc = construction_agent.construct_document_with_ai("NDA", metadata)
        print("Constructed Document:", constructed_doc)
        """

if __name__ == '__main__':
    main()