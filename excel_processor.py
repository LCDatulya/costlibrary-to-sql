"""Module for processing Excel data files."""

import pandas as pd
from typing import Tuple, Optional, Dict
from config import HEADER_ROW, REQUIRED_COLUMNS

class ExcelProcessor:
    """Handles Excel file processing and data extraction."""
    
    def __init__(self, file_path: str, error_logger):
        """
        Initialize Excel processor.
        
        Args:
            file_path: Path to Excel file
            error_logger: Logger for errors
        """
        self.file_path = file_path
        self.error_logger = error_logger
        self.excel_file = pd.ExcelFile(file_path)
    
    def find_column_indices(self, headers) -> Tuple[Optional[int], ...]:
        """
        Find indices of required columns case-insensitively.
        
        Args:
            headers: List of column headers
            
        Returns:
            Tuple of column indices (item, unit, national_price, sa_price)
        """
        headers = [str(h).strip().lower() if pd.notna(h) else '' for h in headers]
        
        return (
            next((i for i, h in enumerate(headers) if 'item' in h), None),
            next((i for i, h in enumerate(headers) if 'unit' in h), None),
            next((i for i, h in enumerate(headers) if 'national' in h), None),
            next((i for i, h in enumerate(headers) if 'sa' in h), None)
        )
    
    @staticmethod
    def get_max_price(national_price, sa_price) -> float:
        """
        Compare national and SA prices and return the higher value.
        
        Args:
            national_price: National price value
            sa_price: SA price value
            
        Returns:
            Maximum price between the two values
        """
        def parse_price(price) -> float:
            """Parse price value with error handling."""
            try:
                return float(price) if pd.notna(price) else 0
            except (ValueError, TypeError):
                return 0
        
        return max(parse_price(national_price), parse_price(sa_price))
    
    def process_sheet(self, sheet_name: str) -> pd.DataFrame:
        """
        Process a single sheet from the Excel file.
        
        Args:
            sheet_name: Name of sheet to process
            
        Returns:
            DataFrame containing processed sheet data
        """
        return pd.read_excel(
            self.file_path,
            sheet_name=sheet_name,
            header=HEADER_ROW
        )
    
    @staticmethod
    def is_valid_row(row) -> bool:
        """
        Check if row should be processed (starts with letter).
        
        Args:
            row: DataFrame row
            
        Returns:
            Boolean indicating if row is valid
        """
        first_cell = str(row.iloc[0]).strip()
        return bool(first_cell and first_cell[0].isalpha())