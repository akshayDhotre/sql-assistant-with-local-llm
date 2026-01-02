"""
SQL database executor module

Author: Akshay Dhotre
July 2024
"""

import sqlite3
from typing import Tuple, List, Any


def get_database_connection(db_file_name: str) -> Tuple[object, object]:
    """
    Establish database connection and return connection and cursor.
    
    Args:
        db_file_name: Path to SQLite database file
        
    Returns:
        Tuple of (connection, cursor)
    """
    db_connection = sqlite3.connect(db_file_name)
    return db_connection, db_connection.cursor()


def create_table(db_cursor: object, db_create_query: str) -> None:
    """
    Create a table in the database.
    
    Args:
        db_cursor: Database cursor object
        db_create_query: CREATE TABLE SQL statement
    """
    db_cursor.execute(db_create_query)
    print("Database table created")


def execute_query(db_cursor: object, query_string: str) -> Any:
    """
    Execute a single SQL query.
    
    Args:
        db_cursor: Database cursor object
        query_string: SQL query to execute
        
    Returns:
        Query results
    """
    response = db_cursor.execute(query_string)
    return response


def execute_queries(db_cursor: object, query_list: List[str]) -> None:
    """
    Execute multiple SQL queries sequentially.
    
    Args:
        db_cursor: Database cursor object
        query_list: List of SQL queries
    """
    for query_string in query_list:
        db_cursor.execute(query_string)
    print(f'Executed {len(query_list)} queries.')


def commit_db_changes(db_connection: object) -> None:
    """
    Commit database changes.
    
    Args:
        db_connection: Database connection object
    """
    db_connection.commit()
    print("Committed the changes")


def close_db_connection(db_connection: object) -> None:
    """
    Close database connection.
    
    Args:
        db_connection: Database connection object
    """
    db_connection.close()
    print("Closed the database connection")
