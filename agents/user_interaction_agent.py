from openai import OpenAI
from Repos.Personal.affinityPractice.multiAgentWorkflow.utils.utils import log_action, load_api_key

client = OpenAI()
client.api_key = load_api_key()

class UserInteractionAgent:
    def __init__(self):
        self.agent_id = 'user_agent_id'
        self.system_prompt = (
            "You are a User Interaction Agent. Your role is to manage user queries, "
            "direct tasks to appropriate agents, and maintain a seamless user experience."
            " Use exact keywords 'search' to initiate a search and 'construct' to initiate document construction."
        )
        self.few_shot_examples = [
            {"role": "user", "content": "I need to find information on due process."},
            {"role": "assistant", "content": "Using 'search' to find information on due process."},
            {"role": "user", "content": "Can you help me create a non-disclosure agreement?"},
            {"role": "assistant", "content": "Using 'construct' to create a non-disclosure agreement."}
        ]
        # Add an example for returning an invalid search result from QA agent for user input / reattempt
        self.few_shot_examples.extend([
            {"role": "user", "content": "The QA agent found inconsistencies in the search results."},
            {"role": "assistant", "content": "Logging inconsistency. Please confirm which response best suits your needs, or provide new details for another attempt."}
        ])
        self.conversation_history = []

    def complete_metadata(self, user_input, metadata_schema):
        for field in metadata_schema.keys():
            if metadata_schema[field] is None:
                # Assume user_input could already fill some fields in metadata_schema
                # More complex logic could parse user_input or ask questions
                metadata_schema[field] = f"Sample data for {field}"  # Placeholder logic
                
                # Example of pseudo-code logic:
                # if field in user_input: metadata_schema[field] = extract_from_input(user_input, field)

        return metadata_schema

    def handle_user_input(self, user_input):
        log_action(f"Received user input: {user_input}")
        self.conversation_history.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.few_shot_examples,
            ] + self.conversation_history
        )
        
        assistant_response = response.choices[0].message.content
        log_action(f"Response from User Interaction Agent: {assistant_response}")
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response
    
    def handle_assistant_input(self, assistant_input):
        log_action(f"Received assistant input: {assistant_input}")
        self.conversation_history.append({"role": "assistant", "content": assistant_input})
        
        print(f"Request from assistant: {assistant_input}")
        return input("Your response:")