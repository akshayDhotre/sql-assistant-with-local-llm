"""
SQL query generation module

This module handles SQL query generation with safety checks.
"""

from typing import Optional, Tuple


def clean_sql_response(response: str) -> str:
    """
    Clean and extract SQL query from LLM response.
    
    Removes markdown code blocks and extra whitespace.
    
    Args:
        response: Raw LLM response
        
    Returns:
        Cleaned SQL query
    """
    # Remove markdown code blocks if present
    if response.startswith("```sql"):
        response = response[6:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    
    # Clean up whitespace
    response = response.strip()
    
    return response


def parse_sql_query(response: str) -> Optional[str]:
    """
    Parse and extract valid SQL from LLM response.
    
    Args:
        response: LLM response text
        
    Returns:
        Extracted SQL query or None
    """
    cleaned = clean_sql_response(response)
    
    # Find the first SELECT statement
    if "SELECT" in cleaned.upper():
        idx = cleaned.upper().find("SELECT")
        return cleaned[idx:]
    
    return cleaned if cleaned else None
