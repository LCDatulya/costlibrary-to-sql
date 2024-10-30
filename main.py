"""Main application module for the data ingestion tool."""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from typing import Optional, Dict

from config import (
    DISCIPLINE_MAP, MAIN_WINDOW_SIZE, EXCEL_FILETYPES, 
    DB_FILETYPES
)
from log_windows import SQLLogWindow, PlainTextLogWindow, ErrorLogWindow
from database_operations import DatabaseManager
from excel_processor import ExcelProcessor

class DataIngestionApp:
    """Main application class for Excel data ingestion."""
    
    def __init__(self, master):
        """
        Initialize the application.
        
        Args:
            master: Root tkinter window
        """
        self.master = master
        self.master.title("Excel Data Ingestion Tool")
        self.master.geometry(MAIN_WINDOW_SIZE)
        
        # Initialize variables
        self.discipline = tk.StringVar()
        self.db_path = tk.StringVar()
        self.excel_path: Optional[str] = None
        
        # Create UI elements
        self._create_widgets()
        
        # Initialize loggers
        self.sql_log = SQLLogWindow(self.master)
        self.plain_log = PlainTextLogWindow(self.master)
        self.error_log = ErrorLogWindow(self.master)
        
        # Show initial information
        self._show_initial_message()
    
    def _create_widgets(self):
        """Create and arrange UI widgets."""
        # Discipline selection
        tk.Label(self.master, text="Select your discipline:").pack(pady=10)
        for discipline in DISCIPLINE_MAP.keys():
            tk.Radiobutton(
                self.master,
                text=discipline,
                variable=self.discipline,
                value=discipline
            ).pack()
        
        # Buttons
        tk.Button(
            self.master,
            text="Select/Create Database",
            command=self.select_database
        ).pack(pady=10)
        
        tk.Button(
            self.master,
            text="Select Excel File",
            command=self.select_excel
        ).pack(pady=10)
        
        tk.Button(
            self.master,
            text="Process Data",
            command=self.process_data
        ).pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.master, text="")
        self.status_label.pack(pady=10)
    
    def _show_initial_message(self):
        """Display initial information message."""
        messagebox.showinfo(
            "Information",
            "Please select an Excel file with headers in row 6. "
            "Required columns: 'Item', 'Unit', 'National Price', 'SA Price'"
        )
    
    def select_database(self):
        """Handle database file selection."""
        path = filedialog.asksaveasfilename(
            title="Select or Create Database File",
            filetypes=DB_FILETYPES,
            defaultextension=".db"
        )
        if path:
            self.db_path.set(path)
            self.status_label.config(text=f"Database: {os.path.basename(path)}")
            
            # Initialize database
            db_manager = DatabaseManager(path, self.sql_log, self.error_log)
            db_manager.initialize_database()
    
    def select_excel(self):
        """Handle Excel file selection."""
        path = filedialog.askopenfilename(filetypes=EXCEL_FILETYPES)
        if path:
            self.excel_path = path
            self.status_label.config(text=f"Excel: {os.path.basename(path)}")
    
    def process_data(self):
        """Process the Excel data and insert into database."""
        # Validate inputs
        if not self._validate_inputs():
            return
        
        try:
            # Initialize processors
            excel_proc = ExcelProcessor(self.excel_path, self.error_log)
            db_manager = DatabaseManager(
                self.db_path.get(),
                self.sql_log,
                self.error_log
            )
            
            # Get discipline ID
            discipline_id = DISCIPLINE_MAP.get(self.discipline.get())
            category_counter = 0
            found_categories = {}
            
            # Process each sheet
            for sheet_name in excel_proc.excel_file.sheet_names:
                self._process_sheet(
                    excel_proc,
                    db_manager,
                    sheet_name,
                    discipline_id,
                    category_counter,
                    found_categories
                )
            
            # Log results
            self._log_results(found_categories)
            messagebox.showinfo("Success", "Data processing completed successfully.")
            
        except Exception as e:
            self.error_log.log(f"Error processing data: {str(e)}")
    
    def _validate_inputs(self) -> bool:
        """
        Validate required inputs before processing.
        
        Returns:
            Boolean indicating if inputs are valid
        """
        if not self.discipline.get():
            self.error_log.log("Error: Please select a discipline.")
            return False
        if not self.db_path.get():
            self.error_log.log("Error: Please select a database file.")
            return False
        if not self.excel_path:
            self.error_log.log("Error: Please select an Excel file.")
            return False
        return True
    
    def _process_sheet(self, excel_proc: ExcelProcessor, 
                      db_manager: DatabaseManager,
                      sheet_name: str, 
                      discipline_id: str,
                      category_counter: int,
                      found_categories: Dict[str, str]) -> int:
        """
        Process a single sheet from the Excel file.
        
        Args:
            excel_proc: ExcelProcessor instance
            db_manager: DatabaseManager instance
            sheet_name: Name of sheet to process
            discipline_id: Current discipline ID
            category_counter: Counter for category IDs
            found_categories: Dict to track found categories
            
        Returns:
            Updated category counter
        """
        self.plain_log.log(f"Processing sheet: {sheet_name}")
        
        # Process sheet
        df = excel_proc.process_sheet(sheet_name)
        
        # Log invalid rows
        invalid_rows = excel_proc.get_invalid_rows(df)
        if invalid_rows:
            self.plain_log.log(
                f"Skipping invalid rows in sheet {sheet_name}: "
                f"rows {', '.join(map(str, invalid_rows))}"
            )
        
        # Find column indices
        column_indices = excel_proc.find_column_indices(df.columns)
        if None in column_indices[:2]:  # Check item and unit columns
            self.error_log.log(
                f"Required columns not found in sheet {sheet_name}. "
                "Skipping sheet."
            )
            return category_counter
        
        current_category_id = None
        rows_processed = 0
        
        # Process each row
        for idx, row in df.iterrows():
            # Process row
            processed_row = excel_proc.process_row(row, column_indices)
            if not processed_row:
                continue
            
            if processed_row['type'] == 'category':
                # Handle category
                category_counter += 1
                current_category_id = f"{category_counter:03d}"
                
                # Insert category
                db_manager.insert_category(
                    current_category_id,
                    processed_row['name'],
                    discipline_id
                )
                
                # Track found category
                found_categories[current_category_id] = processed_row['name']
                
            elif processed_row['type'] == 'item' and current_category_id:
                # Handle item
                max_price = excel_proc.get_max_price(
                    processed_row['national_price'],
                    processed_row['sa_price']
                )
                
                # Insert item
                db_manager.insert_cost_element(
                    processed_row['name'],
                    processed_row['unit'],
                    max_price,
                    current_category_id
                )
                
                rows_processed += 1
        
        self.plain_log.log(
            f"Processed {rows_processed} items in sheet {sheet_name}"
        )
        return category_counter
    
    def _log_results(self, found_categories: Dict[str, str]):
        """
        Log processing results.
        
        Args:
            found_categories: Dictionary of found categories
        """
        if found_categories:
            self.plain_log.log("Categories processed:")
            for category_id, category_name in found_categories.items():
                self.plain_log.log(f"  {category_id}: {category_name}")
        else:
            self.plain_log.log("No categories were processed.")

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = DataIngestionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()