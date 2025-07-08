from tkinter import ttk

class WelcomeView:
    def __init__(self, master, controller):
        self.frame = ttk.Frame(master)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        title_label = ttk.Label(self.frame, text="AI Quiz Game", 
                              style="Title.TLabel")
        title_label.pack(pady=(20, 40))
        
        # Name entry
        name_frame = ttk.Frame(self.frame)
        name_frame.pack(pady=10)
        
        ttk.Label(name_frame, text="Enter your name:").packside ()
        self.name_entry = ttk.Entry(name_frame, font=("Helvetica", 14))
        self.name_entry.packside  ()
        
        # Start button
        start_button = ttk.Button(self.frame, text="Start Game", 
                                command=self.start_game)
        start_button.pack(pady=20)

    def start_game(self):
        name = self.name_entry.get().strip()
        if name:
            self.controller.start_game(name)
        else:
            self.controller.show_error("Please enter your name!")

    def show(self):
        self.frame.pack(fillexpand=True)

    def hide(self):
        self.frame.pack_forget()