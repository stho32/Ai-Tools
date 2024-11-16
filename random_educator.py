import os
import sys
import random
import argparse
from PyPDF2 import PdfReader
from Lib.pdf_audio_tools import call_gpt, text_to_speech, play_audio, get_random_pdf, extract_text_from_pdf

def prepare_content_with_gpt4(text, source_info):
    system_message = "Du bist ein erfahrener Lehrer/Trainer. Deine Aufgabe ist es, den gegebenen Text zu korrigieren, zu erklären und zusammenzufassen. Bitte sprich Deutsch."
    user_message = (
        f"Bitte erkläre den Inhalt, indem du ein kurzes Inhaltsverzeichnis erstellst, dann gehst du durch dieses Verzeichnis und erklärst die Details zu jedem Punkt. "
        f"Fasse am Ende nochmal zusammen, worum es ging. Beginne mit der Erwähnung der Quelle: {source_info}\n\nHier ist der Text:\n\n{text}"
    )
    return call_gpt(system_message, user_message, model="gpt-4")

def random_text_reader(text_dir, num_pages=3):
    # Get all text files in the directory
    text_files = [f for f in os.listdir(text_dir) if f.endswith('.txt')]
    
    if not text_files:
        print(f"[ERROR] No text files found in {text_dir}")
        return None, None

    # Select a random text file
    random_file = random.choice(text_files)
    file_path = os.path.join(text_dir, random_file)
    print(f"[INFO] Selected file: {random_file}")

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

    print(f"[INFO] Reading {num_pages} pages starting from page {start_page + 1}")

    source_info = f"From {random_file} page {start_page + 1}ff"
    return selected_text, source_info

def random_pdf_reader(pdf_dir, num_pages=3):
    try:
        # Choose a random PDF file
        pdf_path = get_random_pdf(pdf_dir)
        pdf_name = os.path.basename(pdf_path)
        print(f"[INFO] Selected PDF: {pdf_path}")

        # Determine the number of pages in the PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            total_pages = len(pdf_reader.pages)

        # Choose a random starting page
        start_page = random.randint(0, max(0, total_pages - num_pages))
        print(f"[INFO] Reading {num_pages} pages starting from page {start_page + 1}")

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
        print("[INFO] Selected: PDF")
        selected_text, source_info = random_pdf_reader(pdf_dir, num_pages)
    else:
        print("[INFO] Selected: Text file")
        selected_text, source_info = random_text_reader(text_dir, num_pages)

    if selected_text and source_info:
        # Process the text with GPT-4
        processed_text = prepare_content_with_gpt4(selected_text, source_info)
        print("[INFO] Processed text:")
        print(processed_text)

        # Convert to speech
        audio_file = text_to_speech(processed_text)

        # Play the audio
        play_audio(audio_file)
    else:
        print("[ERROR] Failed to select and process text.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random Educator: Process and read random PDF or text files.")
    parser.add_argument("pdf_directory", help="Directory containing PDF files")
    parser.add_argument("text_directory", help="Directory containing text files")
    parser.add_argument("--num_pages", type=int, default=3, help="Number of pages to read (default: 3)")
    parser.add_argument("--loop", type=int, help="Number of iterations (if not specified, runs indefinitely)")

    args = parser.parse_args()

    iteration = 1
    while True:
        print(f"\n[INFO] Iteration {iteration}")
        random_educator(args.pdf_directory, args.text_directory, args.num_pages)
        
        if args.loop and iteration >= args.loop:
            break
        
        iteration += 1