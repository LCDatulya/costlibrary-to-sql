"""Module containing logging window classes for the application."""

import tkinter as tk
from tkinter import scrolledtext
from config import LOG_WINDOW_SIZE

class BaseLogWindow:
    """Base class for all logging windows."""
    
    def __init__(self, master, title):
        """
        Initialize a log window.
        
        Args:
            master: Parent tkinter window
            title: Window title
        """
        self.window = tk.Toplevel(master)
        self.window.title(title)
        self.window.geometry(LOG_WINDOW_SIZE)
        self.text_area = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            width=70, 
            height=20
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    def log(self, message):
        """
        Add a message to the log with automatic scrolling.
        
        Args:
            message: Message to log
        """
        self.text_area.insert(tk.END, f"{message}\n\n")
        self.text_area.see(tk.END)

class SQLLogWindow(BaseLogWindow):
    """Window for logging SQL statements."""
    
    def __init__(self, master):
        super().__init__(master, "SQL Log")

class PlainTextLogWindow(BaseLogWindow):
    """Window for logging general text messages."""
    
    def __init__(self, master):
        super().__init__(master, "Database Changes Log")

class ErrorLogWindow(BaseLogWindow):
    """Window for logging error messages."""
    
    def __init__(self, master):
        super().__init__(master, "Error Log")