import os
import sys

#Add the path to the project to run in streamlit's dev environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
import json
from utils.SQLQuery import SQLQuery

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize authentication
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    'config.yaml',
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=True
)

# Create login widget
def setup_login():
    try:
        authenticator.login(
            location='sidebar',
            max_login_attempts=5,
            fields={'Form name':'Login', 'Username':'Username', 'Password':'Password', 'Login':'Submit', 'Captcha':'Captcha'}
        )
    except Exception as e:
        st.error(e)

# Registration widget setup
def register_user():
    try:
        email_of_registered_user, \
        username_of_registered_user, \
        name_of_registered_user = authenticator.register_user(
            location='sidebar',
            roles=['viewer'],
            # pre_authorized=config['pre-authorized']['emails']
            )
        if email_of_registered_user:
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

# Initialize session state for 'register'
if 'register' not in st.session_state:
    st.session_state['register'] = False

# Define a callback to toggle boolean
def toggle_register():
    st.session_state['register'] = not st.session_state['register']

if st.session_state['register']:
    register_user()
    st.sidebar.button(
        label="Back to Login",
        key="back_to_login",
        on_click=toggle_register,
        help="Go back to the login form"
    )
else:
    setup_login()
    if st.session_state['authentication_status'] is not True: 
        st.sidebar.button(
            label="Register New Account",
            key="register_new_account",
            on_click=toggle_register,
            help="Switch to the registration form"
    )
        
# Initialize session state for the success message
if 'show_success_message' not in st.session_state:
    st.session_state['show_success_message'] = False


# Handle login success, failure
if st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.write("# Welcome! Log in on the left to start!")
    st.sidebar.warning('Please enter your username and password, or hit "Register New Account" to sign up')
elif st.session_state['authentication_status']:
    # Trigger the success message display
    st.success('Login successful')
    authenticator.logout(button_name='Log out', location='sidebar')
    st.sidebar.write(f'Welcome, *{st.session_state["name"]}*')


# Initialize globals & render page if user passes authentication
if st.session_state['authentication_status']:

    # Initialize globals
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "This is a demo for agentic database search. It uses a music database that you can examine and query with your functions. Start a conversation to welcome the user so they can try it out. The user cannot see tool messages, so after execute_query, you will need to write a response explaining the result to the user. Be warm, brief, and concise in your responses. Remember to explain the result of any SQL queries to the user, whether it answers their inquiry or not, and offer them a chance to clarify their question if needed once you know the database structure from fetch_db_structure."}]
    if "modality" not in st.session_state:
        st.session_state["modality"] = None
    if "modality_change" not in st.session_state:
        st.session_state["modality_change"] = False

    st.session_state["openai_model"] = "gpt-4o-mini"

class MultiAgentDemo:
    def __init__(self, client, db_path):
        self.client = client
        self.db_path = db_path
        self.messages = st.session_state.get("messages", [])
        self.modality = None # original: st.session_state.get("modality", "Text")
        self.new_message = False
        self.text_response = ""
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "fetch_db_structure",
                    "description": "Retrieve database structure information. Call when you need to determine the database structure prior to making queries, like when a user asks for information. Enables foreign keys and returns a dictionary of database info including tables, schemas, indexes, and foreign keys",
                    "parameters": {},
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_query",
                    "description": "Run an SQL query on the connected database to inform your responses about its contents. Use this when the user asks you about the database or you determine that a database search is the user's goal based on context clues. Remember to write a message to the user explaining the results once the query is complete",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The SQL query written by the assistant to fetch specific data related to the user's request",
                            },
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                }
            }
        ]

    def fetch_db_structure(self):
        with SQLQuery(self.db_path) as sql:
            db_structure = sql.get_db_structure()
        return db_structure
    
    def execute_llm_query(self, query):
        with SQLQuery(self.db_path) as sql:
            try:
                result = sql.llm_query(query)
                return result.fetchall() # gets all list contents that may have been outputted in query results
            except sqlite3.Error as e:
                print(f'Error in execute_llm_query: {e}')
                return f'Error in execute_llm_query: {e}'

    def setup_ui(self):
        st.title("MultiAgent Demo with [SQLite Chinook Database](https://github.com/lerocha/chinook-database)")
        """
        ### Test AI CRUD capabilities with semantic inputs
        """        
        st.sidebar.title("Choose text or speech to start:")
        st.write("*Try searching for artists with the most tracks, greatest hits albums, or anything else you'd expect to find in an iTunes database. Start by choosing an input method on the left.*")
        
        # Initialize modal input selection
        new_modality = st.sidebar.selectbox("Input Modality", ("Text", "Speech"), index=None, placeholder="Choose input mode", label_visibility="hidden", key="modality")

        # Run a check on change of modality to rerun display messages
        if new_modality != self.modality:
            st.session_state["modality_change"] = True
            self.modality = new_modality

    def handle_input(self):
        if st.session_state["modality"] == "Text":
            self.handle_text_input()
        elif st.session_state["modality"] == "Speech":
            self.handle_speech_input()

    def handle_text_input(self):
        text_input = st.chat_input("Type your message", disabled=(self.modality != "Text"))
        if text_input and not self.new_message:
            st.session_state.messages.append({"role": "user", "content": text_input})
            self.new_message = True
            with st.chat_message("user"):
                st.markdown(text_input)

    def handle_speech_input(self):
        audio_input = st.sidebar.audio_input('Click the icon to start and stop recording', disabled=(self.modality != "Speech"))
        if audio_input and not self.new_message:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_input,
                response_format="text"
            )
            st.session_state.messages.append({"role": "user", "content": transcription})
            self.new_message = True
            with st.chat_message("user"):
                st.markdown(transcription)

    def handle_function_input(self, func_name, query, tool_call_id):
        try:
            if func_name == "fetch_db_structure":
                # Write to the user so they know what's going on
                st.markdown("Checking the database structure...")
                schema = self.fetch_db_structure()
                function_call_result_message = {
                    "role": "tool",
                    "content": str(schema),
                    "tool_call_id": tool_call_id
                }
                st.session_state.messages.append(function_call_result_message)
                print("Tool call message constructed and appended to messages")

                print(st.session_state.messages)

                # Run a new assistant response to enable the assistant to call another tool or return a response
                response = self.client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=st.session_state.messages,
                    stream=False,
                    tools=self.tools,
                )
                print(f"Made new Chat Completion based on tool result:\n\n{response}")
                self.process_unstreamed_response(response)


            elif func_name == "execute_query":
                st.markdown("Searching the database for an answer...")
                query_result = self.execute_llm_query(query)
                print(query_result) # debugging

                function_call_result_message = {
                    "role": "tool",
                    "content": str(query_result),
                    "tool_call_id": tool_call_id
                }
                st.session_state.messages.append(function_call_result_message)
                # Print the query and the result as messages
                
                
                # Run a new assistant response to enable the assistant to call another tool or return a response
                response = self.client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=st.session_state.messages,
                    stream=False,
                    tools=self.tools,
                )
                print(f">>Post-query assistant response: {response}")
                self.process_unstreamed_response(response)

        except Exception as e:
            print(f'Error in function call: {e}')
            return st.error(f"Error in function call: {e}")



    def generate_assistant_response(self):
        if self.new_message:
            # bring back stream after confirmed working on no stream
            with st.chat_message("assistant"):
                
                response = self.client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=st.session_state.messages,
                    stream=False,
                    # Add functions for test
                    tools=self.tools,
                )
                self.process_unstreamed_response(response)

                self.new_message = False

    def process_unstreamed_response(self, response):
        # This method is a helper for assistant responses and function calls - same processing occurs when a new chat completion is created if stream=False
        tool_call = None
        # Must append a message with initial tool call before giving tool response to the assistant
        if response.choices[0].message.tool_calls is not None:
            tool_call = response.choices[0].message.tool_calls[0]
        if tool_call is not None: # send to function call if model used a tool
            # print for debug
            print(f'Assistant Tool Call Message: {response.choices[0].message}')
            st.session_state.messages.append(response.choices[0].message)
            # print for debug
            print(tool_call)

            # Set up function call
            tool_call_id = tool_call.id
            func_name = tool_call.function.name
            arguments = tool_call.function.arguments
            arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
            print('Tool Call:\nid>>' + tool_call_id +'\nname>>' + func_name + '\nargs>>' + str(arguments))
            if 'query' in arguments:
                query = arguments.get('query')
            else:
                query = None
                
            print(f"Attempting function call - Name: {func_name}, Query: {query}")
            self.handle_function_input(func_name, query, tool_call_id)

        # If there is no tool call, deal with a standard message
        text_response = response.choices[0].message.content
        if text_response and not tool_call:
            st.markdown(text_response)
            st.session_state.messages.append({"role": "assistant", "content": text_response})
            self.text_response = text_response
            if st.session_state["modality"] == "Speech":
                self.play_audio_response()




    def display_messages(self):
        # to prevent duplicate message displays, only run display_messages when modality changes
        if st.session_state["modality_change"]:
            for message in st.session_state.messages:
                print(message) #debugging

                # Check if the message is a simple code-created message (dictionary)
                if isinstance(message, dict):  # This will catch code-created messages
                    if "role" in message and "content" in message:
                        # Only display user and assistant messages (skip system and tool)
                        if message["role"] not in ["system", "tool"]:
                            with st.chat_message(message["role"]):
                                st.markdown(message["content"])
                
                # Check if the message is a ChatCompletion object (response from OpenAI API)
                elif isinstance(message, object):  # This will catch all messages, but we narrow down with attributes below
                    # Ensure the message has 'choices' and 'content' attributes (typical for OpenAI responses)
                    if hasattr(message, "tool_calls") and hasattr(message, "refusal"):
                        # Ensure it's not a tool call (if tool_calls attribute exists)
                        if not getattr(message, "tool_calls", None):
                            # Display the assistant's message content
                            with st.chat_message(message.role):
                                st.markdown(message.content)

            st.session_state["modality_change"] = False


    def play_audio_response(self):
        if self.new_message and self.modality != "Text":
            # Save TTS audio response
            speech_file_path = Path(__file__).parent / "speech.mp3"
            with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="onyx",
                input=self.text_response
            ) as audio_response:
                audio_response.stream_to_file(speech_file_path)
        
            # Start audio playback on left sidebar
            audio_bytes = open(speech_file_path, 'rb').read()
            st.sidebar.audio(audio_bytes, format="audio/ogg", autoplay=True)

    def main(self):
        self.setup_ui()
        self.display_messages()
        self.handle_input()
        self.generate_assistant_response()
        self.play_audio_response()

# Instantiate and run the app
if st.session_state['authentication_status']:
    client = OpenAI(api_key=OPENAI_API_KEY)
    db_path = "./database/Chinook_Sqlite.sqlite"
    demo = MultiAgentDemo(client, db_path)
    demo.main()