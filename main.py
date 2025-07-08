import tkinter as tk
from app import QuizApp  # Import directly from app.py in same directory

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)  # Pass root window to QuizApp
    root.mainloop()