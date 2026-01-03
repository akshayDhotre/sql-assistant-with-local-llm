"""
Unit tests for application integration and utilities

Author: Akshay Dhotre
"""

import unittest
import tempfile
import sqlite3
import os
from unittest.mock import Mock, patch, MagicMock


class TestApplicationIntegration(unittest.TestCase):
    """Test application integration and workflows."""
    
    def setUp(self):
        """Set up test database and resources."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create test database with schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                grade TEXT,
                gpa REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT UNIQUE,
                credits INTEGER
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO students VALUES (1, 'Alice', 20, 'A', 3.8)")
        cursor.execute("INSERT INTO students VALUES (2, 'Bob', 21, 'B', 3.2)")
        cursor.execute("INSERT INTO students VALUES (3, 'Charlie', 19, 'A', 3.9)")
        
        cursor.execute("INSERT INTO courses VALUES (1, 'Python Programming', 'CS101', 3)")
        cursor.execute("INSERT INTO courses VALUES (2, 'Database Design', 'CS201', 4)")
        
        conn.commit()
        self.conn = conn
        self.cursor = cursor
    
    def tearDown(self):
        """Clean up test database."""
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_full_query_flow(self):
        """Test complete flow from question to SQL to results."""
        from sql.validator import validate_query
        from sql.generator import parse_sql_query
        
        # Simulate LLM response
        llm_response = "```sql\nSELECT * FROM students WHERE age > 19\n```"
        
        # Clean and parse
        from sql.generator import clean_sql_response
        cleaned = clean_sql_response(llm_response)
        parsed = parse_sql_query(cleaned)
        
        # Validate
        is_valid, msg = validate_query(parsed)
        self.assertTrue(is_valid)
        
        # Execute
        result = self.cursor.execute(parsed)
        rows = result.fetchall()
        
        self.assertEqual(len(rows), 2)  # Alice and Charlie
    
    def test_unsafe_query_detection_flow(self):
        """Test detection of unsafe queries throughout pipeline."""
        from security.sql_guardrails import SQLGuardrails
        from sql.validator import validate_query
        
        unsafe_query = "SELECT * FROM students; DROP TABLE students"
        
        # Security check should fail
        is_safe, msg = SQLGuardrails.check_query_safety(unsafe_query)
        self.assertFalse(is_safe)
        
        # Validator should also fail
        is_valid, msg = validate_query(unsafe_query)
        self.assertFalse(is_valid)
    
    def test_schema_introspection_integration(self):
        """Test schema introspection with actual database."""
        from sql.schema_introspector import (
            get_all_tables, get_table_schema, get_table_columns
        )
        
        # Get all tables
        tables = get_all_tables(self.cursor)
        self.assertIn('students', tables)
        self.assertIn('courses', tables)
        
        # Get schema
        students_schema = get_table_schema(self.cursor, 'students')
        self.assertIn('CREATE TABLE', students_schema)
        self.assertIn('students', students_schema)
        
        # Get columns
        columns = get_table_columns(self.cursor, 'students')
        col_names = [col['name'] for col in columns]
        self.assertIn('id', col_names)
        self.assertIn('name', col_names)
        self.assertIn('age', col_names)
    
    def test_complex_query_execution(self):
        """Test execution of complex queries."""
        # Test JOIN query
        join_query = """
            SELECT s.name, c.name as course_name 
            FROM students s, courses c 
            LIMIT 2
        """
        
        from sql.validator import validate_query
        is_valid, msg = validate_query(join_query)
        self.assertTrue(is_valid)
        
        result = self.cursor.execute(join_query)
        rows = result.fetchall()
        self.assertGreater(len(rows), 0)
    
    def test_aggregation_query(self):
        """Test aggregation queries."""
        agg_query = "SELECT AVG(age) as average_age FROM students"
        
        from sql.validator import validate_query
        is_valid, msg = validate_query(agg_query)
        self.assertTrue(is_valid)
        
        result = self.cursor.execute(agg_query)
        avg_age = result.fetchone()[0]
        self.assertIsNotNone(avg_age)
        self.assertGreater(avg_age, 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in various scenarios."""
    
    def test_malformed_sql_syntax(self):
        """Test handling of malformed SQL."""
        from sql.validator import validate_sql_syntax
        
        # Test with unmatched quotes which the validator can catch
        malformed = "SELECT * FROM users WHERE name = 'test"
        is_valid, msg = validate_sql_syntax(malformed)
        # Should detect unmatched quotes
        self.assertFalse(is_valid)
        self.assertIsNotNone(msg)
    
    def test_injection_attempt_handling(self):
        """Test handling of SQL injection attempts."""
        from security.sql_guardrails import SQLGuardrails
        
        # These are the injection patterns that SQLGuardrails is designed to catch
        injection_queries = [
            "SELECT * FROM users UNION SELECT * FROM admins",
            "SELECT * FROM users; DELETE FROM users;",
            "SELECT * FROM users WHERE id = 1; -- DROP TABLE users",
        ]
        
        for query in injection_queries:
            is_safe, msg = SQLGuardrails.check_query_safety(query)
            self.assertFalse(is_safe, f"Failed to detect injection in: {query}")
    
    def test_empty_result_handling(self):
        """Test handling of queries with no results."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = temp_db.name
        temp_db.close()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("CREATE TABLE empty_table (id INT)")
            
            # Query empty table
            result = cursor.execute("SELECT * FROM empty_table")
            rows = result.fetchall()
            
            self.assertEqual(len(rows), 0)
            
            conn.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestDataValidation(unittest.TestCase):
    """Test data validation and sanitization."""
    
    def test_query_sanitization(self):
        """Test query sanitization removes harmful patterns."""
        from security.sql_guardrails import SQLGuardrails
        
        # Query with comments
        query_with_comments = """
            SELECT * FROM users -- This is a comment
            WHERE id = 1 /* inline comment */
        """
        
        sanitized = SQLGuardrails.sanitize_query(query_with_comments)
        
        self.assertNotIn("--", sanitized)
        self.assertNotIn("/*", sanitized)
        self.assertNotIn("*/", sanitized)
    
    def test_keyword_filtering(self):
        """Test filtering of dangerous keywords."""
        from sql.validator import check_dangerous_keywords
        
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER']
        
        for keyword in dangerous_keywords:
            query = f"{keyword} TABLE users"
            is_safe, msg = check_dangerous_keywords(query)
            self.assertFalse(is_safe)
            self.assertIn(keyword, msg)
    
    def test_query_type_checking(self):
        """Test verification that only SELECT queries are allowed."""
        from sql.validator import is_select_query, validate_query
        
        select_query = "SELECT * FROM users"
        insert_query = "INSERT INTO users VALUES (1, 'test')"
        update_query = "UPDATE users SET name = 'test'"
        
        self.assertTrue(is_select_query(select_query))
        self.assertFalse(is_select_query(insert_query))
        self.assertFalse(is_select_query(update_query))
        
        # Full validation
        is_valid, msg = validate_query(select_query)
        self.assertTrue(is_valid)
        
        is_valid, msg = validate_query(insert_query)
        self.assertFalse(is_valid)


class TestPromptSanitization(unittest.TestCase):
    """Test prompt generation with various inputs."""
    
    def test_prompt_with_special_characters(self):
        """Test prompt generation with special characters in input."""
        from llm.prompts import get_sql_generation_prompt
        
        schema = "CREATE TABLE users (id INT, `special-col` VARCHAR(100))"
        question = "Find users with name like 'O'Brien'"
        
        prompt = get_sql_generation_prompt(schema, question)
        
        # Should handle special characters safely
        self.assertIn(schema, prompt)
        self.assertIn(question, prompt)
    
    def test_prompt_with_large_schema(self):
        """Test prompt generation with large schema."""
        from llm.prompts import get_sql_generation_prompt
        
        # Create a large schema with multiple tables
        schema = "\n".join([
            f"CREATE TABLE table_{i} (id INT, data VARCHAR(100))"
            for i in range(10)
        ])
        
        question = "Show all data"
        prompt = get_sql_generation_prompt(schema, question)
        
        self.assertIn(schema, prompt)
        self.assertIn(question, prompt)


if __name__ == '__main__':
    unittest.main()
