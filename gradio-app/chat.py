import gradio as gr
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

def predict(message, history):
    # Ensure history format is correct
    history_openai_format = [{"role": "user", "content": msg.get("content", msg)} if isinstance(msg, dict) else {"role": "user", "content": msg} for msg in history]
    # Append the current message
    history_openai_format.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=history_openai_format,
        temperature=1.0,
        stream=True
    )

    partial_message = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            partial_message += chunk.choices[0].delta.content
            yield partial_message

gr.ChatInterface(predict, type="messages").launch() # pass share=True to launch() if you want a public link
