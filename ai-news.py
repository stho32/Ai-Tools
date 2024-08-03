import os
import json
import hashlib
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
import io
import time
import re
from bs4 import BeautifulSoup
import tiktoken
import requests

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Configuration for URLs and keywords
NEWS_SOURCES = [
    {"url": "https://www.cursor.com/blog", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://changelog.cursor.sh/", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://aider.chat/blog/", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://big-agi.com/blog", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://www.builder.io/", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://codesubmit.io/blog/ai-code-tools", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]}
]

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
    with open(filename, 'w', newline='\n') as f:  # Ensure newlines are written correctly
        json.dump(state, f, indent=2)  # Use indentation for better readability

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

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_gpt4_analysis(content, url, keywords):
    print(f"[DEBUG] Starting GPT-4o analysis for {url}")
    keywords_str = ", ".join(keywords)
    system_message = "You are an AI assistant capable of analyzing web content and extracting relevant information about artificial intelligence."
    user_message = f"Please analyze the following new content from {url} and provide a summary of the latest news and developments related to artificial intelligence, focusing on these keywords: {keywords_str}. Highlight the most recent and important AI developments. Here's the new content:\n\n{content}"

    # Calculate token counts
    system_tokens = num_tokens_from_string(system_message, "cl100k_base")
    user_tokens = num_tokens_from_string(user_message, "cl100k_base")
    total_tokens = system_tokens + user_tokens

    # If total tokens exceed limit, truncate the content
    if total_tokens > 128000:
        max_content_tokens = 128000 - system_tokens - num_tokens_from_string(f"Please analyze the following new content from {url} and provide a summary of the latest news and developments related to artificial intelligence, focusing on these keywords: {keywords_str}. Highlight the most recent and important AI developments. Here's the new content:\n\n", "cl100k_base")
        content_encoding = tiktoken.get_encoding("cl100k_base")
        truncated_content = content_encoding.decode(content_encoding.encode(content)[:max_content_tokens])
        user_message = f"Please analyze the following new content from {url} and provide a summary of the latest news and developments related to artificial intelligence, focusing on these keywords: {keywords_str}. Highlight the most recent and important AI developments. Here's the new content:\n\n{truncated_content}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        print(f"[DEBUG] Successfully received GPT-4o analysis for {url}")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[DEBUG] Error during GPT-4o analysis for {url}: {e}")
        return None

def text_to_speech(text):
    print("[DEBUG] Starting text-to-speech conversion")
    MAX_CHARS = 4000  # Slightly less than the 4096 limit to be safe
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
    print("[DEBUG] Attempting to play audio")
    if audio_contents:
        try:
            combined_audio = AudioSegment.empty()
            for content in audio_contents:
                audio = AudioSegment.from_mp3(io.BytesIO(content))
                combined_audio += audio
            play(combined_audio)
            print("[DEBUG] Audio playback completed")
        except Exception as e:
            print(f"[DEBUG] Error playing audio: {e}")
    else:
        print("[DEBUG] No audio content to play")

def process_source(source):
    url = source["url"]
    keywords = source["keywords"]
    print(f"[DEBUG] Processing source: {url}")
    
    previous_state = load_previous_content(url)
    previous_content = previous_state["content"]
    
    html_content = get_website_content(url)
    if html_content:
        print(f"[DEBUG] Content fetched for {url}, cleaning HTML")
        cleaned_content = clean_html(html_content)
        
        new_content = get_content_diff(previous_content, cleaned_content)
        
        if new_content.strip():  # Check if there's any non-whitespace content
            print(f"[DEBUG] New content found, starting analysis")
            analysis = get_gpt4_analysis(new_content, url, keywords)
            if analysis:
                print(f"[DEBUG] Analysis completed for {url}")
                print("\nAnalysis:")
                print(analysis)
                
                print("\n[DEBUG] Starting text-to-speech conversion")
                audio_contents = text_to_speech(analysis)
                if audio_contents:
                    print("[DEBUG] Text-to-speech conversion successful, playing audio")
                    play_audio(audio_contents)
                else:
                    print("[DEBUG] Failed to convert text to speech")
            else:
                print(f"[DEBUG] Failed to generate an analysis for {url}")
        else:
            print(f"[DEBUG] No new content found for {url}")
        
        save_current_content(url, cleaned_content)
    else:
        print(f"[DEBUG] Failed to fetch the content from {url}")

def main():
    print("[DEBUG] Starting main function")
    
    for i, source in enumerate(NEWS_SOURCES, 1):
        print(f"\n[DEBUG] Processing source {i} of {len(NEWS_SOURCES)}")
        process_source(source)
        
        if i < len(NEWS_SOURCES):
            print("\n[DEBUG] Waiting before processing next source")
            time.sleep(5)  # Wait 5 seconds before processing the next source
    
    print("[DEBUG] All sources processed")

if __name__ == "__main__":
    print("[DEBUG] Script started")
    main()
    print("[DEBUG] Script completed")