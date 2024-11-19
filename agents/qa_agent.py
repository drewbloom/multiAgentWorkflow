from openai import OpenAI
from Repos.Personal.affinityPractice.multiAgentWorkflow.utils.utils import log_action, load_api_key

client = OpenAI()
client.api_key = load_api_key()

class QA_Agent:
    def __init__(self):
        self.agent_id = 'qa_agent_id'
        self.system_prompt = (
            "Act as a QA Agent. Analyze search output for consistency and quality. "
            "Your task is to assess if multiple versions of the output are talking about the same topic. "
            "Confirm consistency or request clarification if needed."
        )
        self.few_shot_examples = [
            {
                "role": "user",
                "content": "Validate search outputs: ['Result A', 'Result A slightly altered', 'Result A with minor changes']"
            },
            {
                "role": "assistant",
                "content": "All results are speaking about the same topic. Consistency confirmed."
            },
            {
                "role": "user",
                "content": "Validate search outputs: ['Result A', 'Different Result B', 'Another Different Result C']"
            },
            {
                "role": "assistant",
                "content": "The outputs vary. Unable to confirm consistency. Please review."
            }
        ]

    def verify_output_with_ai(self, task_outputs):
        log_action(f"Verifying outputs with AI: {task_outputs}")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.few_shot_examples,
                {"role": "user", "content": f"Validate search outputs: {task_outputs}"}
            ]
        )

        result = response.choices[0].message.content
        log_action(f"QA Validation Result: {result}")
        
        return result