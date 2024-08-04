import os
import random
import json
import hashlib
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from openai import OpenAI
from pydub import AudioSegment
import io
import sys
import time

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

def play_audio(audio_contents, output_filename="output.mp3"):
    print("[DEBUG] Saving audio")
    if audio_contents:
        try:
            combined_audio = AudioSegment.empty()
            for content in audio_contents:
                audio = AudioSegment.from_mp3(io.BytesIO(content))
                combined_audio += audio
            combined_audio.export(output_filename, format="mp3")
            print(f"[DEBUG] Audio saved as {output_filename}")
            return output_filename
        except Exception as e:
            print(f"[DEBUG] Error saving audio: {e}")
            return None
    else:
        print("[DEBUG] No audio content to save")
        return None

def get_website_content(url):
    print(f"[DEBUG] Attempting to fetch content from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"[DEBUG] Successfully fetched content from {url}")
        return response.text
    except requests.RequestException as e:
        print(f"[DEBUG] Error fetching the website {url}: {e}")
        return None

def clean_html(html_content):
    print("[DEBUG] Cleaning HTML content")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines and join with newline characters
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    print("[DEBUG] HTML content cleaned")
    return text

def hash_content(content):
    return hashlib.md5(content.encode()).hexdigest()

def get_state_filename(url):
    return f"state_{hash_content(url)}.json"

def load_previous_content(url):
    filename = get_state_filename(url)
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"content": "", "last_processed": None}

def save_current_content(url, content):
    filename = get_state_filename(url)
    state = {
        "content": content,
        "last_processed": time.time()
    }
    with open(filename, 'w', newline='\n') as f:
        json.dump(state, f, indent=2)

def get_content_diff(previous_content, current_content):
    if not previous_content:
        return current_content
    
    previous_lines = previous_content.split('\n')
    current_lines = current_content.split('\n')
    
    diff = []
    for line in current_lines:
        if line not in previous_lines:
            diff.append(line)
    
    return '\n'.join(diff)