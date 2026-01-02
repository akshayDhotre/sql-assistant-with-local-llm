"""
SQL query validation module

This module provides functions to validate SQL queries for syntax and safety.
"""

import re
from typing import Tuple, Optional


# Dangerous SQL keywords for basic safety checks
DANGEROUS_KEYWORDS = [
    'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 
    'INSERT', 'UPDATE', 'CREATE', 'MODIFY'
]


def is_select_query(query: str) -> bool:
    """
    Check if query is a SELECT query.
    
    Args:
        query: SQL query string
        
    Returns:
        True if query starts with SELECT
    """
    return query.strip().upper().startswith('SELECT')


def check_dangerous_keywords(query: str) -> Tuple[bool, Optional[str]]:
    """
    Check if query contains potentially dangerous SQL keywords.
    
    Args:
        query: SQL query string
        
    Returns:
        Tuple of (is_safe, message)
    """
    upper_query = query.upper()
    
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in upper_query:
            return False, f"Query contains potentially dangerous keyword: {keyword}"
    
    return True, None


def validate_sql_syntax(query: str) -> Tuple[bool, Optional[str]]:
    """
    Basic SQL syntax validation.
    
    Args:
        query: SQL query string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query:
        return False, "Query is empty"
    
    # Basic bracket matching
    open_parens = query.count('(')
    close_parens = query.count(')')
    if open_parens != close_parens:
        return False, "Unmatched parentheses"
    
    # Check for quotes matching
    single_quotes = query.count("'")
    if single_quotes % 2 != 0:
        return False, "Unmatched single quotes"
    
    return True, None


def validate_query(query: str, allow_unsafe: bool = False) -> Tuple[bool, str]:
    """
    Comprehensive query validation.
    
    Args:
        query: SQL query to validate
        allow_unsafe: Allow unsafe queries for testing
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not query:
        return False, "Query is empty"
    
    # Check if it's a SELECT query (read-only)
    if not is_select_query(query):
        return False, "Only SELECT queries are supported"
    
    # Check for dangerous keywords
    if not allow_unsafe:
        is_safe, msg = check_dangerous_keywords(query)
        if not is_safe:
            return False, msg
    
    # Validate syntax
    is_valid, msg = validate_sql_syntax(query)
    if not is_valid:
        return False, msg
    
    return True, "Query is valid"
