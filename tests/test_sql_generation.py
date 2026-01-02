"""
Unit tests for SQL generation module

Author: Akshay Dhotre
"""

import unittest
from sql.validator import validate_query, is_select_query, check_dangerous_keywords
from sql.generator import clean_sql_response, parse_sql_query
from security.sql_guardrails import SQLGuardrails


class TestSQLValidator(unittest.TestCase):
    """Test SQL query validation."""
    
    def test_valid_select_query(self):
        """Test that valid SELECT query passes validation."""
        query = "SELECT * FROM Students WHERE Age > 18"
        is_valid, msg = validate_query(query)
        self.assertTrue(is_valid)
    
    def test_invalid_drop_query(self):
        """Test that DROP query fails validation."""
        query = "DROP TABLE Students"
        is_valid, msg = validate_query(query)
        self.assertFalse(is_valid)
    
    def test_empty_query(self):
        """Test that empty query fails validation."""
        query = ""
        is_valid, msg = validate_query(query)
        self.assertFalse(is_valid)
    
    def test_is_select_query(self):
        """Test SELECT query detection."""
        self.assertTrue(is_select_query("SELECT * FROM Users"))
        self.assertFalse(is_select_query("INSERT INTO Users VALUES (1, 'John')"))
    
    def test_dangerous_keywords(self):
        """Test dangerous keyword detection."""
        query = "DELETE FROM Users"
        is_safe, msg = check_dangerous_keywords(query)
        self.assertFalse(is_safe)


class TestSQLGenerator(unittest.TestCase):
    """Test SQL query generation utilities."""
    
    def test_clean_markdown_code_block(self):
        """Test cleaning markdown code blocks."""
        response = "```sql\nSELECT * FROM Users\n```"
        cleaned = clean_sql_response(response)
        self.assertNotIn("```", cleaned)
        self.assertTrue("SELECT" in cleaned)
    
    def test_parse_sql_query(self):
        """Test SQL query parsing."""
        response = "Some text before\nSELECT * FROM Users WHERE id = 1"
        parsed = parse_sql_query(response)
        self.assertTrue(parsed.startswith("SELECT"))


class TestSQLGuardrails(unittest.TestCase):
    """Test SQL security guardrails."""
    
    def test_union_injection_detection(self):
        """Test UNION-based SQL injection detection."""
        query = "SELECT * FROM Users WHERE id = 1 UNION SELECT * FROM Admins"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertFalse(is_safe)
    
    def test_safe_select_query(self):
        """Test that safe SELECT query passes."""
        query = "SELECT * FROM Users WHERE age > 18"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertTrue(is_safe)
    
    def test_sanitize_query(self):
        """Test SQL sanitization."""
        query = "SELECT * FROM Users; -- comment\nDROP TABLE Users"
        sanitized = SQLGuardrails.sanitize_query(query)
        self.assertNotIn("--", sanitized)
        self.assertNotIn(";", sanitized.rstrip())


if __name__ == '__main__':
    unittest.main()
