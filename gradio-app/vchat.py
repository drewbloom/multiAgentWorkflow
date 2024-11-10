import gradio as gr
from openai import OpenAI
import os
import whisper
from dotenv import load_dotenv
import base64
import io

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

def predict(message, history, is_voice=False):
    # Handle voice input
    if is_voice:
        message = speech_to_text(message)

    # Prepare the history in the correct format
    history_openai_format = [{"role": "user", "content": msg.get("content", msg)} if isinstance(msg, dict) else {"role": "user", "content": msg} for msg in history]
    history_openai_format.append({"role": "user", "content": message})

    # Query OpenAI API
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=history_openai_format,
        temperature=1.0,
        stream=True
    )

    # Generate partial response
    partial_message = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            partial_message += chunk.choices[0].delta.content
            yield partial_message

def speech_to_text(audio_file):
    # Check if the input is a base64 string or a file path
    if isinstance(audio_file, str) and audio_file.startswith("data:audio"):
        # Decode base64 audio (assuming it's in WAV or MP3 format)
        audio_data = base64.b64decode(audio_file.split(",")[1])
        audio_file = io.BytesIO(audio_data)  # Convert base64 to a file-like object
    elif isinstance(audio_file, str) and os.path.exists(audio_file):
        # If the input is a file path, use it directly
        audio_file = open(audio_file, 'rb')  # Open the file in binary mode
    
    # Load the Whisper model
    model = whisper.load_model("base")

    # Load the audio into a waveform (as a numpy array)
    audio_array = whisper.load_audio(audio_file)

    # Transcribe the audio (passing the waveform directly)
    result = model.transcribe(audio_array)

    # Return the transcription result
    return result["text"]

# Gradio interface for both text and voice input
with gr.Blocks() as demo:
    with gr.Row():
        text_input = gr.Textbox(label="Enter your message", lines=1)
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Speak your message")

    with gr.Row():
        is_voice = gr.Checkbox(label="Switch to Voice Input", value=False)

    output = gr.Chatbot(type='messages')

    # Bind the predict function to both text and voice input
    text_input.submit(predict, [text_input, output, is_voice], output)
    audio_input.change(predict, [audio_input, output, is_voice], output)

demo.launch()