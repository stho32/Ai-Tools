import os
import sys
import random
import argparse
from PyPDF2 import PdfReader
from Lib.pdf_audio_tools import (
    get_random_pdf,
    extract_text_from_pdf,
    call_gpt,
    text_to_speech,
    play_audio
)

def prepare_content_with_gpt4(text, pdf_path):
    print("[DEBUG] Preparing content with GPT-4")
    system_message = """Du bist ein erfahrener Lehrer/Trainer. Deine Aufgabe ist es, den gegebenen Text zu korrigieren, zu erklären und zusammenzufassen. Bitte sprich Deutsch und sei präzise in deinen Erklärungen.

Bearbeite den Text nach diesem Schema:
1. Nenne zuerst die Quelle des Textes.
2. Erstelle ein kurzes Inhaltsverzeichnis der Hauptpunkte.
3. Gehe durch jeden Punkt des Inhaltsverzeichnisses und leite jeden inhaltlichen Abschnitt mit einer relevanten Frage ein. Beantworte dann diese Frage ausführlich mit den Details aus dem Text.
4. Fasse am Ende die Kernaussagen des Textes zusammen, indem du fragst: "Was sind die wichtigsten Erkenntnisse aus diesem Text?"
5. Stelle eine abschließende Frage wie: "Wie können wir dieses Wissen in der Praxis anwenden?" oder "Welche Verbindungen gibt es zu verwandten Themen?" und beantworte sie basierend auf dem Inhalt des Textes."""

    user_message = f"Hier ist der Text aus der Quelle '{pdf_path}':\n\n{text}"
    return call_gpt(system_message, user_message)

def random_pdf_reader(directory, num_pages=5, loop=False):
    while True:
        try:
            pdf_path = get_random_pdf(directory)
            print(f"[INFO] Selected PDF: {pdf_path}")

            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                total_pages = len(pdf_reader.pages)

            start_page = random.randint(0, max(0, total_pages - num_pages))
            print(f"[INFO] Starting from page {start_page + 1}")

            text = extract_text_from_pdf(pdf_path, start_page, num_pages)

            prepared_content = prepare_content_with_gpt4(text, pdf_path)
            if prepared_content:
                print("[INFO] Content prepared successfully")
                
                audio_contents = text_to_speech(prepared_content)
                if audio_contents:
                    print("[INFO] Text-to-speech conversion successful")
                    play_audio(audio_contents)
                else:
                    print("[ERROR] Failed to convert text to speech")
            else:
                print("[ERROR] Failed to prepare content with GPT-4")

            if not loop:
                break

        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {str(e)}")
            if not loop:
                sys.exit(1)
            else:
                print("[INFO] Continuing to next PDF due to loop mode")

def main():
    parser = argparse.ArgumentParser(description="Random PDF Reader")
    parser.add_argument("pdf_directory", help="Directory containing PDF files")
    parser.add_argument("--num_pages", type=int, default=5, help="Number of pages to read (default: 5)")
    parser.add_argument("--loop", action="store_true", help="Continuously read random PDFs")
    args = parser.parse_args()

    random_pdf_reader(args.pdf_directory, args.num_pages, args.loop)

if __name__ == "__main__":
    main()