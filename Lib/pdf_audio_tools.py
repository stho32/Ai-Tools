import os
import json
import requests
from bs4 import BeautifulSoup
import openai
import anthropic
import re
from typing import Optional, List, Dict, Any, Tuple
import random
import hashlib
import io
import sys
import time

# Initialize the OpenAI client
openai_client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))
# Initialize the Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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
            pdf_reader = openai.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            end_page = min(start_page + num_pages, total_pages)
            for page_num in range(start_page, end_page):
                page_text = pdf_reader.pages[page_num].extract_text()
                text += page_text + "\n\n"
                
                # Save each page's text to a separate file for debugging
                debug_filename = f"page_{page_num + 1}_debug.txt"
                with open(debug_filename, 'w', encoding='utf-8') as debug_file:
                    debug_file.write(page_text)
                print(f"[DEBUG] Saved text from page {page_num + 1} to {debug_filename}")
    except Exception as e:
        print(f"[ERROR] An error occurred while reading the PDF: {str(e)}")
        sys.exit(1)
    return text

def call_gpt(system_message, user_message):
    config = load_config()
    model_config = config.get('model_config', {'provider': 'openai', 'model': 'gpt-4'})
    provider = model_config.get('provider', 'openai')
    model = model_config.get('model', 'gpt-4')

    print(f"[DEBUG] Calling {provider} API with model {model}")
    try:
        if provider == 'openai':
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        elif provider == 'anthropic':
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            return response.content[0].text
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except Exception as e:
        print(f"[ERROR] Error calling {provider} API: {str(e)}")
        return None

def text_to_speech(text):
    print("[DEBUG] Converting text to speech")
    MAX_CHARS = 4096  # OpenAI's TTS API limit
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= MAX_CHARS:
            current_chunk += " " + word if current_chunk else word
        else:
            chunks.append(current_chunk)
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)

    audio_contents = []

    for i, chunk in enumerate(chunks):
        try:
            print(f"[DEBUG] Converting chunk {i+1} of {len(chunks)}")
            response = openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=chunk
            )
            audio_contents.append(response.content)
            print(f"[DEBUG] Successfully converted chunk {i+1}")
        except Exception as e:
            print(f"[DEBUG] Error during text-to-speech conversion for chunk {i+1}: {e}")
    
    return audio_contents


def chunk_to_speech(text):
    print("[DEBUG] Converting text to speech")
    try:
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        random_voice = random.choice(voices)
        print(f"[DEBUG] Selected voice: {random_voice}")
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice=random_voice,
            input=text
        )
        return response.content
    
    except Exception as e:
        print(f"[DEBUG] Error during text-to-speech conversion: {e}")
    
    return None


def play_audio(audio_contents, output_filename="output.mp3"):
    print("[DEBUG] Processing audio")
    if audio_contents:
        try:
            combined_audio = AudioSegment.empty()
            for content in audio_contents:
                audio = AudioSegment.from_mp3(io.BytesIO(content))
                combined_audio += audio
            
            # Save the audio file
            combined_audio.export(output_filename, format="mp3")
            print(f"[DEBUG] Audio saved as {output_filename}")
            
            # Play the audio
            print("[DEBUG] Playing audio")
            play(combined_audio)
            
            return output_filename
        except Exception as e:
            print(f"[DEBUG] Error processing or playing audio: {e}")
            return None
    else:
        print("[DEBUG] No audio content to process")
        return None

def get_website_content(url):
    print(f"[DEBUG] Attempting to fetch content from {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            error_msg = f"HTTP {response.status_code}"
            print(f"[DEBUG] Error fetching the website {url}: {error_msg}")
            return None, error_msg
        print(f"[DEBUG] Successfully fetched content from {url}")
        return response.text, None
    except requests.RequestException as e:
        error_msg = str(e)
        print(f"[DEBUG] Error fetching the website {url}: {error_msg}")
        return None, error_msg

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

def get_state_directory():
    status_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.ai-news-status')
    os.makedirs(status_dir, exist_ok=True)
    return status_dir

def get_state_filename(url):
    return os.path.join(get_state_directory(), f"state_{hash_content(url)}.json")

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
    """
    Identifies new content by comparing current with previous content.
    Optimized for finding new/modified content only, ignoring deletions.
    Uses sets for efficient comparison and handles similar content as new.
    """
    if not previous_content:
        return current_content
    
    # Split into lines and create a set for efficient lookup
    previous_lines = set(previous_content.split('\n'))
    current_lines = current_content.split('\n')
    
    # Keep track of new content while maintaining order
    new_content = []
    
    # Process each current line
    for line in current_lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # If line is not in previous content, it's new
        if line not in previous_lines:
            new_content.append(line)
    
    return '\n'.join(new_content) if new_content else ""

def load_config(config_path=None):
    """Load configuration from file."""
    if config_path is None:
        # Try to load the main config file first, fall back to example if it doesn't exist
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai-news-config.json')
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai-news-config.example.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"[ERROR] Failed to load configuration from {config_path}: {str(e)}")
        return {"categories": {}, "news_sources": []}

def get_gpt4_analysis(content, url, keywords, category):
    print(f"[DEBUG] Starting GPT-4 analysis for {url} in category {category}")
    keywords_str = ", ".join(keywords)
    
    # Get system message from config
    config = load_config()
    categories = config.get('categories', {})
    category_config = categories.get(category, {})
    system_message = category_config.get('system_message', "You are an expert technology analyst.")
    
    user_message = """Please analyze the following new content from {0} and provide a summary of the latest developments related to {1}, 
    focusing on these keywords: {2}. Highlight the most important updates and their practical implications for developers.
    Provide the summary in German.
    
    Content to analyze:
    {3}
    """.format(url, category, keywords_str, content)

    return call_gpt(system_message, user_message)