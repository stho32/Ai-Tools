import os
import sys
import random
import argparse
from PyPDF2 import PdfReader
from pdf_audio_tools import (
    get_random_pdf,
    extract_text_from_pdf,
    call_gpt,
    text_to_speech,
    play_audio
)

def prepare_content_with_gpt4(text):
    print("[DEBUG] Preparing content with GPT-4")
    system_message = "Du bist ein erfahrener Lehrer/Trainer. Deine Aufgabe ist es, den gegebenen Text zu korrigieren, zu erklären und zusammenzufassen. Bitte sprich Deutsch."
    user_message = f"Bitte erkläre den Inhalt, indem du ein kurzes Inhaltsverzeichnis erstellst, dann gehst du durch dieses Verzeichnis und erklärst die Details zu jedem Punkt. Fasse am Ende nochmal zusammen, worum es ging. Hier ist der Text:\n\n{text}"
    return call_gpt(system_message, user_message)

def random_pdf_reader(directory, num_pages=5, loop=False):
    while True:
        try:
            # Choose a random PDF file
            pdf_path = get_random_pdf(directory)
            print(f"[INFO] Selected PDF: {pdf_path}")

            # Determine the number of pages in the PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                total_pages = len(pdf_reader.pages)

            # Choose a random starting page
            start_page = random.randint(0, max(0, total_pages - num_pages))
            print(f"[INFO] Starting from page {start_page + 1}")

            # Extract text from the selected pages
            text = extract_text_from_pdf(pdf_path, start_page, num_pages)

            # Prepare content with GPT-4
            prepared_content = prepare_content_with_gpt4(text)
            if prepared_content:
                print("[INFO] Content prepared successfully")
                
                # Convert prepared content to speech
                audio_contents = text_to_speech(prepared_content)
                if audio_contents:
                    print("[INFO] Text-to-speech conversion successful")
                    
                    # Play the audio
                    play_audio(audio_contents)
                else:
                    print("[ERROR] Failed to convert text to speech")
            else:
                print("[ERROR] Failed to prepare content with GPT-4")

            if not loop:
                break

        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random PDF Reader")
    parser.add_argument("pdf_directory", help="Directory containing PDF files")
    parser.add_argument("--num_pages", type=int, default=5, help="Number of pages to read (default: 5)")
    parser.add_argument("--loop", action="store_true", help="Continuously read random PDFs")
    args = parser.parse_args()

    random_pdf_reader(args.pdf_directory, args.num_pages, args.loop)