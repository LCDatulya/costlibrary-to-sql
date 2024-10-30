"""Configuration settings and constants for the data ingestion application."""

# Database table schemas
COST_CATEGORIES_SCHEMA = '''
CREATE TABLE IF NOT EXISTS cost_categories (
    category_id TEXT PRIMARY KEY, 
    category_name TEXT, 
    discipline_id INTEGER,
    FOREIGN KEY (disciplines_id) REFERENCES disciplines(discipline_id)
)
'''

COST_ELEMENTS_SCHEMA = '''
CREATE TABLE IF NOT EXISTS cost_elements (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    item_name TEXT, 
    unit TEXT, 
    price REAL, 
    category_id TEXT,
    FOREIGN KEY (category_id) REFERENCES cost_categories(category_id)
)
'''

# Mapping of discipline codes to IDs
DISCIPLINE_MAP = {
    'e': '1',
    'f': '2',
    'd': '3',
    'm': '4',
    'h': '5',
    'a': '6'
}

# Window configurations
MAIN_WINDOW_SIZE = "400x400"
LOG_WINDOW_SIZE = "600x400"

# Required Excel columns
REQUIRED_COLUMNS = ['item', 'unit', 'national price', 'sa price']

# File extension filters
EXCEL_FILETYPES = [("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
DB_FILETYPES = [("All Files", "*.*")]

# Excel configuration
HEADER_ROW = 5  # 0-based index for row 6