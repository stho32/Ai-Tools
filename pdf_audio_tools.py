import os
import random
from PyPDF2 import PdfReader
from openai import OpenAI
from pydub import AudioSegment
import io
import sys

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_random_pdf(directory):
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    if not pdf_files:
        raise ValueError(f"No PDF files found in {directory}")
    return os.path.join(directory, random.choice(pdf_files))

def extract_text_from_pdf(pdf_path, start_page, num_pages):
    print(f"[DEBUG] Extracting text from PDF, starting at page {start_page}")
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            total_pages = len(pdf_reader.pages)
            end_page = min(start_page + num_pages, total_pages)
            for page_num in range(start_page, end_page):
                text += pdf_reader.pages[page_num].extract_text() + "\n\n"
    except Exception as e:
        print(f"[ERROR] An error occurred while reading the PDF: {str(e)}")
        sys.exit(1)
    return text

def call_gpt(system_message, user_message, model="gpt-4"):
    print(f"[DEBUG] Calling GPT model: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[DEBUG] Error during GPT call: {e}")
        return None

def text_to_speech(text):
    print("[DEBUG] Converting text to speech")
    MAX_CHARS = 4000  # OpenAI's TTS API limit
    chunks = [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
    audio_contents = []

    for i, chunk in enumerate(chunks):
        try:
            print(f"[DEBUG] Converting chunk {i+1} of {len(chunks)}")
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=chunk
            )
            audio_contents.append(response.content)
            print(f"[DEBUG] Successfully converted chunk {i+1}")
        except Exception as e:
            print(f"[DEBUG] Error during text-to-speech conversion for chunk {i+1}: {e}")
    
    return audio_contents

def play_audio(audio_contents):
    print("[DEBUG] Playing audio")
    if audio_contents:
        try:
            combined_audio = AudioSegment.empty()
            for content in audio_contents:
                audio = AudioSegment.from_mp3(io.BytesIO(content))
                combined_audio += audio
            combined_audio.export("output.mp3", format="mp3")
            print("[DEBUG] Audio saved as output.mp3")
            # You can add code here to play the audio if desired
        except Exception as e:
            print(f"[DEBUG] Error saving audio: {e}")
    else:
        print("[DEBUG] No audio content to play")