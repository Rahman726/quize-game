from tkinter import ttk
from constants.colors import COLORS

def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure("TFrame", background=COLORS["background"])
    style.configure("TLabel", background=COLORS["background"], 
                   foreground=COLORS["text"], font=("Helvetica", 12))
    # ... rest of the style configurations
    
    return style