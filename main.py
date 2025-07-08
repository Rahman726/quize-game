import tkinter as tk
from app import QuizApp

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)  # This should now work
    root.mainloop()