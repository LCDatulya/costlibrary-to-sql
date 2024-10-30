"""Module for processing Excel data files."""

import pandas as pd
import re
from typing import Tuple, Optional, Dict
from config import HEADER_ROW, REQUIRED_COLUMNS

class ExcelProcessor:
    """Handles Excel file processing and data extraction."""
    
    # Move validation patterns here from TextValidator
    INVALID_PATTERNS = [
        r'^\s*\*{1,}',  # Rows starting with asterisks
        r'^\s*NOTE[S]?\s*:',  # Notes
        r'^\s*TO BE\s+',  # "TO BE USED" type phrases
        r'^\s*GUIDE\s*:?',  # Guide references
        r'^\s*IMPORTANT\s*:',  # Important notices
        r'^\s*WARNING\s*:',  # Warnings
        r'^\s*CAUTION\s*:',  # Cautions
        r'^\s*N\.?B\.?\s*:',  # N.B. or NB:
        r'^\s*\(?see\s+',  # References starting with "see"
    ]
    
    # Compile patterns for better performance
    COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in INVALID_PATTERNS]
    
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
    
    def get_invalid_rows(self, df: pd.DataFrame) -> list:
        """
        Get list of invalid row indices.
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of invalid row indices
        """
        invalid_rows = []
        for idx, row in df.iterrows():
            if not self.is_valid_row(row):
                invalid_rows.append(idx)
        return invalid_rows
    
    def process_row(self, row, column_indices: Tuple[int, ...]) -> Optional[Dict]:
        """
        Process a single row from the Excel file.
        
        Args:
            row: DataFrame row
            column_indices: Tuple of column indices
            
        Returns:
            Dictionary with processed data or None if row is invalid
        """
        item_idx, unit_idx, national_idx, sa_idx = column_indices
        
        # Get first cell content
        first_cell = str(row.iloc[0]).strip()
        
        # Skip if empty or doesn't start with letter
        if not first_cell or not first_cell[0].isalpha():
            return None
            
        # Clean the text
        cleaned_text = self.clean_text(first_cell)
        if not cleaned_text:
            return None
            
        # Determine if this is a category or item
        if self.is_valid_category_name(cleaned_text):
            return {
                'type': 'category',
                'name': cleaned_text
            }
            
        # Process as item if valid
        if self.is_valid_item_name(cleaned_text):
            return {
                'type': 'item',
                'name': cleaned_text,
                'unit': str(row.iloc[unit_idx]).strip() if unit_idx is not None else '',
                'national_price': row.iloc[national_idx] if national_idx is not None else 0,
                'sa_price': row.iloc[sa_idx] if sa_idx is not None else 0
            }
            
        return None
    
    def is_valid_category_name(self, text: str) -> bool:
        """
        Check if text is a valid category name.
        
        Args:
            text: Text to validate
            
        Returns:
            Boolean indicating if text is a valid category name
        """
        if not text or len(text.strip()) < 2:
            return False
            
        # Check against invalid patterns
        for pattern in self.COMPILED_PATTERNS:
            if pattern.search(text):
                return False
        
        # Must start with a letter or number
        if not text[0].isalnum():
            return False
            
        # Should not be just numbers
        if text.replace('.', '').isdigit():
            return False
            
        return True
    
    def is_valid_item_name(self, text: str) -> bool:
        """
        Check if text is a valid item name.
        
        Args:
            text: Text to validate
            
        Returns:
            Boolean indicating if text is a valid item name
        """
        if not text or len(text.strip()) < 2:
            return False
            
        # Check against invalid patterns
        for pattern in self.COMPILED_PATTERNS:
            if pattern.search(text):
                return False
        
        return True
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean text by removing unwanted characters and standardizing format.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text or None if text is invalid
        """
        if not text or not isinstance(text, str):
            return None
            
        # Strip whitespace
        text = text.strip()
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        # Remove special characters from start/end
        text = text.strip('*:-.')
        
        # Strip again after removing special characters
        text = text.strip()
        
        return text if text else None
    
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