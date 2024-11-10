from openai import OpenAI
from utils import log_action, load_api_key

client = OpenAI()
client.api_key = load_api_key()

class KnowledgeSearchAgent:
    def __init__(self):
        self.agent_id = 'knowledge_search_agent_id'
        self.system_prompt = "You are a Knowledge Search Agent. Your task is to execute keyword and semantic searches to retrieve relevant legal documents."
        self.few_shot_examples = [
            {"role": "user", "content": "Perform a keyword search for 'due process'."},
            {"role": "assistant", "content": "Executing keyword search and sending results to QA agent for validation."},
            {"role": "user", "content": "Conduct a semantic search for precedents about constitutional rights violations during an arrest."},
            {"role": "assistant", "content": "Performing semantic search and directing outputs to QA agent for consistency checking."}
        ]

    def perform_search(self, query):
        log_action(f"Performing search for query: {query}")
        responses = []
        for i in range(3):  # Execute the search three times
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.few_shot_examples,
                    {"role": "user", "content": query}
                ]
            )
            result = response.choices[0].message.content
            log_action(f"Search result {i+1}: {result}")
            responses.append(result)
        return responses