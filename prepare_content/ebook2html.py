import pyautogui
import time
from PIL import Image
import imagehash
import pytesseract
import os
import argparse

pyautogui.PAUSE = 0.1  # Add a small pause after each PyAutoGUI function call

def are_last_4_images_same(image_hashes):
    if len(image_hashes) < 4:
        return False
    return len(set(image_hashes[-4:])) == 1

def perform_ocr_to_text(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def combine_text_files(text_files):
    combined_text = ""
    for i, text_file in enumerate(text_files):
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_text += content
            if i < len(text_files) - 1:  # Don't add divider after the last file
                combined_text += "\n\n----------------------------------------------------------------------- NEXT PAGE\n\n"
    
    with open('combined_output.txt', 'w', encoding='utf-8') as f:
        f.write(combined_text)
    
    # Delete original text files after combining
    for text_file in text_files:
        os.remove(text_file)

def main(left, top, width, height):
    region = (left, top, width, height)
    
    print("Starting in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print("Starting now!")

    image_hashes = []
    counter = 0
    text_files = []
    image_files = []

    while True:
        try:
            pyautogui.press('space')
            time.sleep(0.2)
            
            screenshot = pyautogui.screenshot(region=region)
            
            image_filename = f"screenshot_{counter}.png"
            screenshot.save(image_filename)
            image_files.append(image_filename)
            
            image_hash = imagehash.average_hash(Image.open(image_filename))
            image_hashes.append(image_hash)
            
            print(f"Saved {image_filename}")

            ocr_text = perform_ocr_to_text(image_filename)
            text_filename = f"text_{counter}.txt"
            with open(text_filename, 'w', encoding='utf-8') as text_file:
                text_file.write(ocr_text)
            
            text_files.append(text_filename)
            print(f"Saved OCR text to {text_filename}")
            
            if are_last_4_images_same(image_hashes):
                print("Last 4 images are the same. Stopping.")
                break
            
            counter += 1

        except pyautogui.FailSafeException:
            print("PyAutoGUI fail-safe triggered. Stopping.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    print("Combining text files...")
    combine_text_files(text_files)
    print("Combined text saved as 'combined_output.txt'")

    # Delete image files and temporary text files
    for image_file in image_files:
        os.remove(image_file)
    for text_file in text_files:
        if os.path.exists(text_file):
            os.remove(text_file)
    print("Deleted original image and text files.")

if __name__ == "__main__":
    # Update this path to where Tesseract is actually installed on your system
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    parser = argparse.ArgumentParser(description="Capture screenshots, perform OCR, and save as HTML.")
    parser.add_argument("left", type=int, help="Left coordinate of the capture region")
    parser.add_argument("top", type=int, help="Top coordinate of the capture region")
    parser.add_argument("width", type=int, help="Width of the capture region")
    parser.add_argument("height", type=int, help="Height of the capture region")
    
    args = parser.parse_args()
    
    main(args.left, args.top, args.width, args.height)