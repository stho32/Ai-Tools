import pyautogui
import time
from PIL import Image, ImageGrab, ImageTk
import imagehash
import pytesseract
import os
import tkinter as tk

pyautogui.PAUSE = 0.1  # Add a small pause after each PyAutoGUI function call

class RegionSelector:
    def __init__(self, master):
        self.master = master
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None

        # Take a screenshot
        self.screenshot = ImageGrab.grab()
        self.tk_image = ImageTk.PhotoImage(self.screenshot)

        self.master.attributes('-fullscreen', True)
        self.master.attributes('-topmost', True)

        self.canvas = tk.Canvas(master, cursor="cross", width=self.screenshot.width, height=self.screenshot.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Display the screenshot on the canvas
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = self.start_y = self.end_x = self.end_y = 0

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_move_press(self, event):
        self.current_x, self.current_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.current_x, self.current_y)

    def on_button_release(self, event):
        self.end_x, self.end_y = (event.x, event.y)
        self.master.quit()

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

def main():
    root = tk.Tk()
    app = RegionSelector(root)
    root.mainloop()

    # After region selection, destroy the window to free the screen
    root.destroy()

    left = int(min(app.start_x, app.end_x))
    top = int(min(app.start_y, app.end_y))
    width = int(abs(app.end_x - app.start_x))
    height = int(abs(app.end_y - app.start_y))

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

            pyautogui.press('space')
            time.sleep(0.2)

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
    
    main()