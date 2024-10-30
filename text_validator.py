"""Module for validating text entries from Excel files."""

import re
from typing import Optional

class TextValidator:
    """Validates text entries from Excel files."""
    
    # Patterns for identifying invalid rows
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
    
    @classmethod
    def is_valid_category_name(cls, text: Optional[str]) -> bool:
        """
        Check if text is a valid category name.
        
        Args:
            text: Text to validate
            
        Returns:
            Boolean indicating if text is a valid category name
        """
        if not text or not isinstance(text, str):
            return False
            
        # Strip whitespace
        text = text.strip()
        
        # Check minimum length (after stripping)
        if len(text) < 2:
            return False
            
        # Check against invalid patterns
        for pattern in cls.COMPILED_PATTERNS:
            if pattern.search(text):
                return False
        
        # Additional checks for valid category names
        # Must start with a letter or number
        if not text[0].isalnum():
            return False
            
        # Should not be just numbers
        if text.replace('.', '').isdigit():
            return False
            
        return True
    
    @classmethod
    def is_valid_item_name(cls, text: Optional[str]) -> bool:
        """
        Check if text is a valid item name.
        
        Args:
            text: Text to validate
            
        Returns:
            Boolean indicating if text is a valid item name
        """
        if not text or not isinstance(text, str):
            return False
            
        # Strip whitespace
        text = text.strip()
        
        # Check minimum length (after stripping)
        if len(text) < 2:
            return False
            
        # Check against invalid patterns
        for pattern in cls.COMPILED_PATTERNS:
            if pattern.search(text):
                return False
        
        return True
    
    @classmethod
    def clean_text(cls, text: Optional[str]) -> Optional[str]:
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