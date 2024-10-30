"""Module handling all database-related operations."""

import sqlite3
from typing import Tuple, Optional, Dict
import pandas as pd
from config import COST_CATEGORIES_SCHEMA, COST_ELEMENTS_SCHEMA

class DatabaseManager:
    """Manages database operations for the application."""
    
    def __init__(self, db_path: str, sql_logger, error_logger):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
            sql_logger: Logger for SQL statements
            error_logger: Logger for errors
        """
        self.db_path = db_path
        self.sql_logger = sql_logger
        self.error_logger = error_logger
    
    def initialize_database(self) -> None:
        """Create necessary database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tables
                cursor.execute(COST_CATEGORIES_SCHEMA)
                self.sql_logger.log(COST_CATEGORIES_SCHEMA)
                
                cursor.execute(COST_ELEMENTS_SCHEMA)
                self.sql_logger.log(COST_ELEMENTS_SCHEMA)
                
                conn.commit()
        except Exception as e:
            self.error_logger.log(f"Error initializing database: {str(e)}")
    
    def insert_category(self, category_id: str, category_name: str, 
                       discipline_id: str) -> None:
        """
        Insert a new category into the database.
        
        Args:
            category_id: Unique identifier for category
            category_name: Name of the category
            discipline_id: Associated discipline ID
        """
        sql = '''INSERT OR IGNORE INTO cost_categories 
                (category_id, category_name, disciplines_id) 
                VALUES (?, ?, ?)'''
        self._execute_sql(sql, (category_id, category_name, discipline_id))
    
    def insert_cost_element(self, item_name: str, unit: str, 
                          price: float, category_id: str) -> None:
        """
        Insert a new cost element into the database.
        
        Args:
            item_name: Name of the item
            unit: Unit of measurement
            price: Price value
            category_id: Associated category ID
        """
        sql = '''INSERT INTO cost_elements
                (item_name, unit, price, category_id)
                VALUES (?, ?, ?, ?)'''
        self._execute_sql(sql, (item_name, unit, price, category_id))
    
    def _execute_sql(self, sql: str, parameters: tuple) -> None:
        """
        Execute SQL statement with error handling and logging.
        
        Args:
            sql: SQL statement to execute
            parameters: Parameters for SQL statement
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, parameters)
                conn.commit()
                self.sql_logger.log(f"Executed SQL: {sql}\nParameters: {parameters}")
        except Exception as e:
            self.error_logger.log(f"Error executing SQL: {str(e)}\nSQL: {sql}")