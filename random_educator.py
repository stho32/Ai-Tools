import os
import sys
import random
from PyPDF2 import PdfReader
from pdf_audio_tools import call_gpt, text_to_speech, play_audio, get_random_pdf, extract_text_from_pdf

def prepare_content_with_gpt4(text, source_info):
    system_message = "You are a helpful assistant that explains and summarizes text in German."
    user_message = (
        f"Please explain and summarize the following text in German. "
        f"Make it engaging and suitable for audio playback. "
        f"Start with mentioning the source: {source_info}\n\n" + text
    )
    return call_gpt(system_message, user_message, model="gpt-4")

def random_text_reader(text_dir, num_pages=3):
    # Get all text files in the directory
    text_files = [f for f in os.listdir(text_dir) if f.endswith('.txt')]
    
    if not text_files:
        print(f"No text files found in {text_dir}")
        return None, None

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

    source_info = f"From {random_file} page {start_page + 1}ff"
    return selected_text, source_info

def random_pdf_reader(pdf_dir, num_pages=3):
    try:
        # Choose a random PDF file
        pdf_path = get_random_pdf(pdf_dir)
        pdf_name = os.path.basename(pdf_path)
        print(f"Selected PDF: {pdf_path}")

        # Determine the number of pages in the PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            total_pages = len(pdf_reader.pages)

        # Choose a random starting page
        start_page = random.randint(0, max(0, total_pages - num_pages))
        print(f"Reading {num_pages} pages starting from page {start_page + 1}")

        # Extract text from the selected pages
        text = extract_text_from_pdf(pdf_path, start_page, num_pages)

        source_info = f"From {pdf_name} page {start_page + 1}ff"
        return text, source_info

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred in random_pdf_reader: {str(e)}")
        return None, None

def random_educator(pdf_dir, text_dir, num_pages=3):
    # Randomly choose between PDF and text file
    is_pdf = random.choice([True, False])

    if is_pdf:
        print("Selected: PDF")
        selected_text, source_info = random_pdf_reader(pdf_dir, num_pages)
    else:
        print("Selected: Text file")
        selected_text, source_info = random_text_reader(text_dir, num_pages)

    if selected_text and source_info:
        # Process the text with GPT-4
        processed_text = prepare_content_with_gpt4(selected_text, source_info)
        print("Processed text:")
        print(processed_text)

        # Convert to speech
        audio_file = text_to_speech(processed_text)

        # Play the audio
        play_audio(audio_file)
    else:
        print("Failed to select and process text.")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python random_educator.py <pdf_directory> <text_directory> [num_pages]")
        sys.exit(1)

    pdf_dir = sys.argv[1]
    text_dir = sys.argv[2]
    num_pages = int(sys.argv[3]) if len(sys.argv) == 4 else 3

    random_educator(pdf_dir, text_dir, num_pages)