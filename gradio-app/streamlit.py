import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

st.title("MultiAgent Demo with SQLite Chinook Database")

"""
In this demo, we try to offer voice and chat input to interface with an assistant who can accomplish database tasks by calling other agents and using tools.  
Our demo uses the simple Chinook database, so asking for top artists, artists with the most tracks, or number of albums are all fair game!
"""

# Add gpt model to client
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

# Add chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "What would you like to do?"}] # system messages still display: [{"role": "system", "content": "This is a demo for a multi-agent database search and document creation."}]

# Display history in chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's up?"):
    # Add message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat container
    with st.chat_message("user"):
        st.markdown(prompt)

# Display assistant response in chat container
with st.chat_message("assistant"):
    stream = client.chat.completions.create(
        model = st.session_state["openai_model"],
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )
    response = st.write_stream(stream)

st.session_state.messages.append({"role": "assistant", "content": response})