import os
import sys
import random
from pdf_audio_tools import call_gpt, text_to_speech, play_audio

def prepare_content_with_gpt4(text):
    system_message = "You are a helpful assistant that explains and summarizes text in German."
    user_message = (
        "Please explain and summarize the following text in German. "
        "Make it engaging and suitable for audio playback:\n\n" + text
    )
    return call_gpt(system_message, user_message, model="gpt-4")

def random_text_reader(text_dir, num_pages=3):
    # Get all text files in the directory
    text_files = [f for f in os.listdir(text_dir) if f.endswith('.txt')]
    
    if not text_files:
        print(f"No text files found in {text_dir}")
        sys.exit(1)

    # Select a random text file
    random_file = random.choice(text_files)
    file_path = os.path.join(text_dir, random_file)
    print(f"Selected file: {random_file}")

    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the content into pages
    pages = content.split("----------------------------------------------------------------------- NEXT PAGE")

    # Select a random starting page
    start_page = random.randint(0, max(0, len(pages) - num_pages))
    
    # Extract the specified number of pages
    selected_pages = pages[start_page:start_page + num_pages]
    selected_text = "\n".join(selected_pages)

    print(f"Reading {num_pages} pages starting from page {start_page + 1}")

    # Process the text with GPT-4
    processed_text = prepare_content_with_gpt4(selected_text)
    print("Processed text:")
    print(processed_text)

    # Convert to speech
    audio_file = text_to_speech(processed_text)

    # Play the audio
    play_audio(audio_file)

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python random_text_reader.py <text_directory> [num_pages]")
        sys.exit(1)

    text_dir = sys.argv[1]
    num_pages = int(sys.argv[2]) if len(sys.argv) == 3 else 3

    random_text_reader(text_dir, num_pages)