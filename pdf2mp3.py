import os
import sys
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from openai import OpenAI
from pydub import AudioSegment
import io

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_path, page_number):
    print(f"[DEBUG] Extracting text from PDF, page {page_number}")
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            if 0 <= page_number < len(pdf_reader.pages):
                text = pdf_reader.pages[page_number].extract_text()
            else:
                print(f"[ERROR] Page {page_number} does not exist in the PDF.")
    except ImportError:
        print("[ERROR] PyCryptodome is required for handling this PDF. Please install it using: pip install pycryptodome")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] An error occurred while reading the PDF: {str(e)}")
        sys.exit(1)
    return text

def clean_text(text):
    print("[DEBUG] Cleaning extracted text")
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def save_page_content(text, pdf_path, page_number):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = f"{base_name}-page-{page_number}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"[DEBUG] Saved page content to {output_file}")

def text_to_speech(text):
    print("[DEBUG] Converting text to speech")
    MAX_CHARS = 4000  # OpenAI's TTS API limit
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

def combine_audio(audio_contents, output_path):
    print("[DEBUG] Combining audio chunks")
    combined_audio = AudioSegment.empty()
    for content in audio_contents:
        audio = AudioSegment.from_mp3(io.BytesIO(content))
        combined_audio += audio
    
    combined_audio.export(output_path, format="mp3")
    print(f"[DEBUG] Audio saved to {output_path}")

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
        print("Usage: python pdf_to_audio.py <path_to_pdf_file> <page_number>")
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