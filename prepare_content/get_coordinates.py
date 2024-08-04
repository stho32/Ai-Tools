import tkinter as tk
from PIL import ImageGrab, ImageTk
import pyautogui

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

        self.canvas = tk.Canvas(master, width=self.screenshot.width, height=self.screenshot.height, cursor="cross")
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

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
        left = min(self.start_x, self.current_x)
        top = min(self.start_y, self.current_y)
        right = max(self.start_x, self.current_x)
        bottom = max(self.start_y, self.current_y)

        print(f"Region: Left: {int(left)}, Top: {int(top)}, Width: {int(right - left)}, Height: {int(bottom - top)}")
        self.master.quit()

def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    app = RegionSelector(root)
    root.mainloop()

if __name__ == "__main__":
    main()