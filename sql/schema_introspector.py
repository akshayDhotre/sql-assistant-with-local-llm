"""
Database schema introspection utilities

This module provides functions to introspect database schema and metadata.
"""

import sqlite3
from typing import List, Dict, Any


def get_table_schema(cursor: object, table_name: str) -> str:
    """
    Get the CREATE TABLE statement for a specific table.
    
    Args:
        cursor: Database cursor object
        table_name: Name of the table
        
    Returns:
        CREATE TABLE statement as string
    """
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()
    return result[0] if result else ""


def get_all_tables(cursor: object) -> List[str]:
    """
    Get list of all table names in the database.
    
    Args:
        cursor: Database cursor object
        
    Returns:
        List of table names
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]


def get_table_columns(cursor: object, table_name: str) -> List[Dict[str, Any]]:
    """
    Get column information for a table.
    
    Args:
        cursor: Database cursor object
        table_name: Name of the table
        
    Returns:
        List of column information dictionaries
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = []
    for row in cursor.fetchall():
        columns.append({
            'name': row[1],
            'type': row[2],
            'notnull': row[3],
            'default': row[4],
            'pk': row[5]
        })
    return columns


def get_database_schema(cursor: object) -> str:
    """
    Get complete database schema information.
    
    Args:
        cursor: Database cursor object
        
    Returns:
        Complete schema as formatted string
    """
    tables = get_all_tables(cursor)
    schema_str = ""
    
    for table in tables:
        schema = get_table_schema(cursor, table)
        if schema:
            schema_str += schema + "\n"
    
    return schema_str
