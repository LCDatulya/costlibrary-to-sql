"""Module for processing Excel data files."""

import pandas as pd
from typing import Tuple, Optional, Dict, List
from config import HEADER_ROW, REQUIRED_COLUMNS
from text_validator import TextValidator

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
        self.text_validator = TextValidator()
    
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
        df = pd.read_excel(
            self.file_path,
            sheet_name=sheet_name,
            header=HEADER_ROW
        )
        
        # Clean column names
        df.columns = [str(col).strip() if pd.notna(col) else '' for col in df.columns]
        
        return df
    
    def validate_row(self, row: pd.Series, is_category: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate a row from the Excel file.
        
        Args:
            row: DataFrame row
            is_category: Boolean indicating if row should be treated as category
            
        Returns:
            Tuple of (is_valid, cleaned_text)
        """
        # Get first cell value
        text = row.iloc[0]
        
        # Clean the text
        cleaned_text = TextValidator.clean_text(text)
        if not cleaned_text:
            return False, None
            
        # Validate based on row type
        if is_category:
            is_valid = TextValidator.is_valid_category_name(cleaned_text)
        else:
            is_valid = TextValidator.is_valid_item_name(cleaned_text)
            
        return is_valid, cleaned_text
    
    def process_row(self, row: pd.Series, column_indices: Tuple[int, ...]) -> Optional[Dict]:
        """
        Process a single row from the Excel file.
        
        Args:
            row: DataFrame row
            column_indices: Tuple of column indices
            
        Returns:
            Dictionary containing processed row data or None if row is invalid
        """
        item_col, unit_col, national_price_col, sa_price_col = column_indices
        
        # Check if row is a category (no unit)
        is_category = pd.isna(row[unit_col]) if unit_col is not None else True
        
        # Validate row
        is_valid, cleaned_text = self.validate_row(row, is_category)
        if not is_valid:
            return None
            
        # Process category row
        if is_category:
            return {
                'type': 'category',
                'name': cleaned_text
            }
            
        # Process item row
        return {
            'type': 'item',
            'name': cleaned_text,
            'unit': row[unit_col] if unit_col is not None else '',
            'national_price': row[national_price_col] if national_price_col is not None else None,
            'sa_price': row[sa_price_col] if sa_price_col is not None else None
        }
    
    def get_invalid_rows(self, df: pd.DataFrame) -> List[int]:
        """
        Get list of invalid row indices for logging purposes.
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of invalid row indices
        """
        invalid_rows = []
        for idx, row in df.iterrows():
            text = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            for pattern in TextValidator.COMPILED_PATTERNS:
                if pattern.search(text):
                    invalid_rows.append(idx + 1)  # Add 1 for Excel row number
                    break
        return invalid_rows