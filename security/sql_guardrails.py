"""
SQL security and guardrails module

This module provides security checks and guardrails for SQL query execution.
"""

from typing import Tuple, Optional
import re


class SQLGuardrails:
    """SQL query safety guardrails."""
    
    # Disallowed patterns
    DISALLOWED_PATTERNS = [
        r';\s*DROP',
        r';\s*DELETE',
        r';\s*TRUNCATE',
        r'UNION.*SELECT',  # Potential SQL injection via UNION
        r'--.*\n',  # SQL comments
        r'/\*.*\*/',  # Multi-line comments
    ]
    
    # Rate limiting
    MAX_QUERIES_PER_MINUTE = 100
    MAX_RESULT_ROWS = 10000
    
    @staticmethod
    def check_query_safety(query: str) -> Tuple[bool, Optional[str]]:
        """
        Perform comprehensive safety check on SQL query.
        
        Args:
            query: SQL query to check
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        # Check for disallowed patterns
        for pattern in SQLGuardrails.DISALLOWED_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Query contains disallowed pattern: {pattern}"
        
        # Check for multiple statements (separated by semicolons)
        statements = [s.strip() for s in query.split(';') if s.strip()]
        if len(statements) > 1:
            return False, "Multiple SQL statements are not allowed"
        
        return True, None
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Sanitize SQL query by removing dangerous patterns.
        
        Args:
            query: SQL query to sanitize
            
        Returns:
            Sanitized query
        """
        # Remove SQL comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Remove trailing semicolons
        query = query.rstrip(';').strip()
        
        return query
