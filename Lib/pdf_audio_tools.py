#!/usr/bin/env python3
import os
import json
import openai
import anthropic
import re
from typing import Optional, List, Dict, Any, Tuple
import random
import io
import sys
import time

# Initialize the OpenAI client
from openai import OpenAI
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

def load_config(config_path=None):
    """
    Load optional configuration from file.

    Used by call_gpt() to read model_config (provider/model selection).
    If no config is found, call_gpt falls back to hard-coded defaults.

    Args:
        config_path: Optional path to a JSON config file. Relative paths
            are resolved against the repo root.
    Returns:
        dict: Parsed config, or empty dict if no file is present.
    """
    if config_path is None:
        return {}

    base_dir = os.path.dirname(os.path.dirname(__file__))
    if not os.path.isabs(config_path):
        config_path = os.path.join(base_dir, config_path)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load configuration from {config_path}: {str(e)}")
        return {}