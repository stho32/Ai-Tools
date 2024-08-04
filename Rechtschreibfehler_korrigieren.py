import os
import sys
from pdf_audio_tools import call_gpt

def process_file(input_file):
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file {input_file} does not exist.")
        sys.exit(1)

    # Create output file names
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_korrigiert.txt"
    output_file_pages = f"{base_name}_korrigiert_Seiten.txt"

    # Delete output files if they already exist
    for file in [output_file, output_file_pages]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted existing file: {file}")

    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the content into pages
    pages = content.split("----------------------------------------------------------------------- NEXT PAGE")

    # Process each page
    total_pages = len(pages)
    for i, page in enumerate(pages, 1):
        print(f"Processing page {i} of {total_pages}")

        # Call GPT to correct the page
        system_message = "You are a helpful assistant that corrects OCR errors in text."
        user_message = (
            "Diese Seite kommt aus einem OCR. Bitte korrigiere alle Erkennungsfehler im Text, "
            "so dass der Inhalt ordentlich und sauber ist. Bitte gib mir nur die korrigierte "
            "Fassung (kein Blabla). Bitte gib mir das Ergebnis auch nicht in einem Codeblock, "
            "sondern einfach plain. Du kannst gerne die Linefeeds korrigieren, so dass es sich "
            "um einen Fließtext handelt.\n\n" + page.strip()
        )
        corrected_page = call_gpt(system_message, user_message, model="gpt-3.5-turbo")

        # Print the corrected page to the console
        print("\nCorrected page:")
        print(corrected_page)
        print("\n" + "="*50 + "\n")

        # Write to the output files
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(corrected_page + "\n\n")

        with open(output_file_pages, 'a', encoding='utf-8') as f:
            f.write(corrected_page + "\n\n")
            if i < total_pages:
                f.write("----------------------------------------------------------------------- NEXT PAGE\n\n")

    print(f"Processing complete. Output files created: {output_file} and {output_file_pages}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Rechtschreibfehler_korrigieren.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    process_file(input_file)
