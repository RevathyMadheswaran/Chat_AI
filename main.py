import os
import streamlit as st
from streamlit_option_menu import option_menu
from groq import Groq
from PIL import Image
from app import (load_gemini_model, load_llama_model,
                 image_captioning, summarize_audio, save_uploaded_file,
                 extract_transcript_details, generate_gemini_content)

# get the current working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="AI Fusion Hub",
    page_icon="🤖",
    layout="centered"
)

with st.sidebar:
    selected = option_menu('Chat with Bot', 
                           ['Gemini',
                            'Llama',
                            'Image Captioning',
                            'Audio Summarization',
                            'YouTube Video Summarization'],
                            menu_icon='robot',icons=['google', 'meta','image-fill','mic-fill','youtube'],
                            default_index=0)
    
# Function to translate roles between Gemini and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role
    
# Gemini chatbot page
if selected == 'Gemini':
    model = load_gemini_model()

    # Initialize chat session in Streamlit if not already present
    if "chat_session_gemini" not in st.session_state: 
        st.session_state.chat_session_gemini = model.start_chat(history=[])

    # Display the chatbot's title on the page
    st.title("🤖 Chat with Gemini")

    # Display the chat history
    for message in st.session_state.chat_session_gemini.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Input field for user's message
    user_prompt = st.chat_input("Ask Gemini...")
    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)

        # Send user's message to Gemini and get the response
        gemini_response = st.session_state.chat_session_gemini.send_message(user_prompt)

        # Display Gemini's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

# Llama chatbot page
if selected == 'Llama':
    llama_model = load_llama_model()

    messages = [
        {"role": "system", "content": "You are a helpful assistant"}
    ]

    # Initialize chat session in Streamlit if not already present
    if "chat_session_llama" not in st.session_state: 
        st.session_state.chat_session_llama = {"history":[], "messages": messages}

    # Display the chatbot's title on the page
    st.title("🦙 Chat with Llama")

    # Display the chat history
    for message in st.session_state.chat_session_llama["history"]:
        with st.chat_message(translate_role_for_streamlit(message["role"])):
            st.markdown(message["text"])

    # Input field for user's message
    user_prompt = st.chat_input("Ask Llama...")
    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)

        # Append the user message to messages
        st.session_state.chat_session_llama["messages"].append({"role": "user", "content": user_prompt})

        # Send user's message to Llama and get the response
        client = Groq()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.chat_session_llama["messages"]
        )
        
        # Adjust accessing the response based on the actual structure
        llama_response = response.choices[0].message.content

        # Update Llama chat session history
        st.session_state.chat_session_llama["history"].append({"role": "user", "text": user_prompt})
        st.session_state.chat_session_llama["history"].append({"role": "assistant", "text": llama_response})

        # Display Llama's response
        with st.chat_message("assistant"):
            st.markdown(llama_response)

# Image captioning page
if selected == "Image Captioning":

    st.title("📷 Snap Narrate")

    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if st.button("Generate Caption"):
        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            resized_img = image.resize((800, 600))
            st.image(resized_img)

        default_prompt = "write a brief caption for this image" 

        # get the caption of the image from the gemini-pro-vision LLM
        caption = image_captioning(default_prompt, image)

        with col2:
            st.info(caption)

# Audio Summarization page
if selected == "Audio Summarization":

    st.title("🎶 Summarize the Audio")

    uploaded_audio = st.file_uploader("Upload Audio File...", type=['wav', 'mp3'])
    if uploaded_audio is not None:
        audio_path = save_uploaded_file(uploaded_audio)  # Save the uploaded file and get the path
        st.audio(audio_path)

        if st.button('Summarize Audio'):
            with st.spinner('Summarizing...'):
                summary_text = summarize_audio(uploaded_audio)
                st.info(summary_text)

# YouTube video Summarization page

prompt="""You are a Youtube video summarizer. You have to take the entire transcript text
from the video and summarize it with bullet points. First, mention the title of the video,
then summarize the entire video with highlighting the keypoints. At the end please include
some conclusion about the video. The entire summarization should be with in 500 words.
Please provide the summary of the text given here: """

if selected == "YouTube Video Summarization":

    st.image("https://img.icons8.com/?size=100&id=108794&format=png&color=000000")
    st.title("YouTube Video Summarization")
    youtube_link = st.text_input("Enter YouTube Video Link:")

    if youtube_link:
        video_id = youtube_link.split("=")[1]
        print(video_id)
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    if st.button("Summarize Video"):
        with st.spinner('Summarizing...'):
            transcript_text= extract_transcript_details(youtube_link)

        if transcript_text:
            summary=generate_gemini_content(transcript_text, prompt)
            st.markdown("# Detailed Notes:")
            st.write(summary)


