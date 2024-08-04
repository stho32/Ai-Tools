import os
import sys
from pdf_audio_tools import (
    extract_text_from_pdf,
    clean_text,
    save_page_content,
    text_to_speech,
    combine_audio
)

def pdf_to_audio(pdf_path, page_number):
    # Generate output path
    base_name = os.path.splitext(pdf_path)[0]
    output_path = f"{base_name}-page-{page_number}.mp3"
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path, page_number)
    
    if not text:
        print("[ERROR] No text extracted from the PDF. Exiting.")
        sys.exit(1)
    
    # Save the page content for debugging
    save_page_content(text, pdf_path, page_number)
    
    # Clean the extracted text
    cleaned_text = clean_text(text)
    
    # Convert text to speech
    audio_contents = text_to_speech(cleaned_text)
    
    # Combine audio chunks and save
    combine_audio(audio_contents, output_path)
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf2mp3.py <path_to_pdf_file> <page_number>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' does not exist.")
        sys.exit(1)
    
    try:
        page_number = int(sys.argv[2])
    except ValueError:
        print("Error: Page number must be an integer.")
        sys.exit(1)
    
    try:
        output_path = pdf_to_audio(pdf_path, page_number)
        print(f"PDF page to Audio conversion completed! Audio saved as: {output_path}")
    except Exception as e:
        print(f"An error occurred during conversion: {str(e)}")
        sys.exit(1)