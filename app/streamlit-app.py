import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize globals
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "This is a demo for a multi-agent database search and document creation. Start a conversation to welcome the user so they can try it out. Be warm, brief, and concise in your responses"}]
if "modality" not in st.session_state:
    st.session_state["modality"] = None
if "modality_change" not in st.session_state:
    st.session_state["modality_change"] = False

st.session_state["openai_model"] = "gpt-4o-mini"

# Current issue:  when switching modality, the message history is lost in "messages". find a fix

class MultiAgentDemo:
    def __init__(self, client):
        self.client = client
        self.messages = st.session_state.get("messages", [])
        self.modality = None # original: st.session_state.get("modality", "Text")
        self.new_message = False
        self.text_response = ""

    def setup_ui(self):
        st.title("MultiAgent Demo with [SQLite Chinook Database](https://github.com/lerocha/chinook-database)")
        """
        ### Test an AI agent's CRUD capabilities with semantic inputs.
        """        
        st.sidebar.title("Choose text or speech to start")
        st.write("*Try searching for artists with the most tracks, greatest hits albums, or anything else you'd expect to find in an iTunes database. Start by choosing an input method on the left.*")
        
        # Initialize modal input selection
        new_modality = st.sidebar.selectbox("Input Modality", ("Text", "Speech"), index=None, placeholder="Choose input mode", label_visibility="hidden", key="modality")

        # Run a check on change of modality to rerun display messages
        if new_modality != self.modality:
            st.session_state["modality_change"] = True
            self.modality = new_modality

        print(st.session_state["modality_change"])

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
        audio_input = st.sidebar.audio_input('Click the icon and start and stop recording', disabled=(self.modality != "Speech"))
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

    def generate_assistant_response(self):
        if self.new_message:
            # stream if text entry
            if st.session_state["modality"] == "Text":
                with st.chat_message("assistant"):
                    
                    stream = self.client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                    
                st.session_state.messages.append({"role": "assistant", "content": response})
                self.new_message = False

            elif st.session_state["modality"] == "Speech":
                # No stream for audio to make logic simpler
                with st.chat_message("assistant"):

                    response = self.client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages                           
                        ],
                        stream=False
                    )
                    text_response = response.choices[0].message.content
                    st.markdown(text_response)

                st.session_state.messages.append({"role": "assistant", "content": text_response})
                self.text_response = text_response
                self.play_audio_response()
                self.new_message = False


    def display_messages(self):
        # to prevent duplicate message displays, only run display_messages when modality changes
        if st.session_state["modality_change"]:
            for message in st.session_state.messages:
                print(message) #debugging
                if message["role"] != "system" and not message["content"].startswith("<few-shot-message>"):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

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
client = OpenAI(api_key=OPENAI_API_KEY)
demo = MultiAgentDemo(client)
demo.main()