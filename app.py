import os
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
import tempfile
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

# get the current working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# set up Google Gemini AI model
genai.configure(api_key=GOOGLE_API_KEY)

# for getting response from gemini model
def load_gemini_model():
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    return gemini_model

# set up Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key = GROQ_API_KEY)

messages = [
        {"role": "system", "content": "You are a helpful assistant"}
    ]

# for getting response from llama model
def load_llama_model():
    llama_model = client.chat.completions.create(model="llama-3.1-8b-instant",
                                                 messages=messages)
    return llama_model

# for getting response from gemini model(image to text)
def image_captioning(prompt, image):
    gemini_flash_model = genai.GenerativeModel("gemini-1.5-flash")
    response = gemini_flash_model.generate_content([prompt, image])
    result = response.text
    return result

# for getting response from gemini model(audio to text)
def summarize_audio(audio_file_path):
    model = genai.GenerativeModel("gemini-1.5-flash")
    mime_type = 'audio/wav'
    audio_file = genai.upload_file(path=audio_file_path,mime_type=mime_type)
    response = model.generate_content(
        [
            "Please summarize the following audio.",
            audio_file
        ]
    )
    return response.text

# Save uploaded file to a temporary file and return the path
def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None
    
# for getting response from gemini-pro model(video to text)

# getting the transcript data from youtube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id=youtube_video_url.split("=")[1]
        
        transcript_text=YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e
    
# getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text,prompt):
    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text

