"""
Unit tests for SQL generation and related modules

Author: Akshay Dhotre
"""

import unittest
import sqlite3
import tempfile
import os
from sql.validator import (
    validate_query, is_select_query, check_dangerous_keywords, 
    validate_sql_syntax
)
from sql.generator import clean_sql_response, parse_sql_query
from sql.executor import (
    get_database_connection, execute_query, execute_queries, 
    commit_db_changes, close_db_connection
)
from sql.schema_introspector import (
    get_table_schema, get_all_tables, get_table_columns, 
    get_database_schema
)
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
    
    def test_is_select_query_with_whitespace(self):
        """Test SELECT query detection with leading whitespace."""
        self.assertTrue(is_select_query("  SELECT * FROM Users"))
        self.assertTrue(is_select_query("\nSELECT * FROM Users"))
    
    def test_dangerous_keywords(self):
        """Test dangerous keyword detection."""
        query = "DELETE FROM Users"
        is_safe, msg = check_dangerous_keywords(query)
        self.assertFalse(is_safe)
        self.assertIn("DELETE", msg)
    
    def test_all_dangerous_keywords(self):
        """Test all dangerous keywords are detected."""
        dangerous = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'INSERT', 'UPDATE', 'CREATE', 'MODIFY']
        for keyword in dangerous:
            query = f"{keyword} TABLE Users"
            is_safe, msg = check_dangerous_keywords(query)
            self.assertFalse(is_safe, f"Failed to detect {keyword}")
    
    def test_safe_keywords(self):
        """Test that safe queries pass keyword check."""
        query = "SELECT * FROM Users WHERE department = 'Sales'"
        is_safe, msg = check_dangerous_keywords(query)
        self.assertTrue(is_safe)
    
    def test_validate_sql_syntax_empty(self):
        """Test validation of empty query."""
        is_valid, msg = validate_sql_syntax("")
        self.assertFalse(is_valid)
        self.assertIn("empty", msg.lower())
    
    def test_validate_sql_syntax_unmatched_parentheses(self):
        """Test validation of unmatched parentheses."""
        is_valid, msg = validate_sql_syntax("SELECT * FROM Users WHERE (id = 1")
        self.assertFalse(is_valid)
        self.assertIn("parenthes", msg.lower())
    
    def test_validate_sql_syntax_unmatched_quotes(self):
        """Test validation of unmatched quotes."""
        is_valid, msg = validate_sql_syntax("SELECT * FROM Users WHERE name = 'John")
        self.assertFalse(is_valid)
        self.assertIn("quote", msg.lower())
    
    def test_validate_sql_syntax_valid(self):
        """Test validation of correct SQL syntax."""
        is_valid, msg = validate_sql_syntax("SELECT * FROM Users WHERE name = 'John'")
        self.assertTrue(is_valid)


class TestSQLGenerator(unittest.TestCase):
    """Test SQL query generation utilities."""
    
    def test_clean_markdown_code_block_sql(self):
        """Test cleaning markdown code blocks with sql tag."""
        response = "```sql\nSELECT * FROM Users\n```"
        cleaned = clean_sql_response(response)
        self.assertNotIn("```", cleaned)
        self.assertIn("SELECT", cleaned)
    
    def test_clean_markdown_code_block_plain(self):
        """Test cleaning plain markdown code blocks."""
        response = "```\nSELECT * FROM Users\n```"
        cleaned = clean_sql_response(response)
        self.assertNotIn("```", cleaned)
        self.assertIn("SELECT", cleaned)
    
    def test_clean_whitespace(self):
        """Test whitespace cleanup."""
        response = "  \n  SELECT * FROM Users  \n  "
        cleaned = clean_sql_response(response)
        self.assertEqual(cleaned, "SELECT * FROM Users")
    
    def test_parse_sql_query_with_prefix(self):
        """Test SQL query parsing with prefix text."""
        response = "Some text before\nSELECT * FROM Users WHERE id = 1"
        parsed = parse_sql_query(response)
        self.assertTrue(parsed.startswith("SELECT"))
    
    def test_parse_sql_query_case_insensitive(self):
        """Test SQL query parsing is case insensitive."""
        response = "Some text\nselect * from users"
        parsed = parse_sql_query(response)
        self.assertIsNotNone(parsed)
        self.assertIn("select", parsed.lower())
    
    def test_parse_sql_query_no_select(self):
        """Test parsing when no SELECT is present."""
        response = "Some text without SQL"
        parsed = parse_sql_query(response)
        self.assertEqual(parsed, "Some text without SQL")
    
    def test_parse_sql_query_empty(self):
        """Test parsing empty response."""
        response = ""
        parsed = parse_sql_query(response)
        self.assertIsNone(parsed)


class TestSQLGuardrails(unittest.TestCase):
    """Test SQL security guardrails."""
    
    def test_union_injection_detection(self):
        """Test UNION-based SQL injection detection."""
        query = "SELECT * FROM Users WHERE id = 1 UNION SELECT * FROM Admins"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertFalse(is_safe)
    
    def test_union_injection_lowercase(self):
        """Test UNION injection detection with lowercase."""
        query = "select * from users union select * from admins"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertFalse(is_safe)
    
    def test_safe_select_query(self):
        """Test that safe SELECT query passes."""
        query = "SELECT * FROM Users WHERE age > 18"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertTrue(is_safe)
    
    def test_safe_join_query(self):
        """Test that safe JOIN query passes."""
        query = "SELECT u.id, o.amount FROM Users u JOIN Orders o ON u.id = o.user_id"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertTrue(is_safe)
    
    def test_comment_injection_single_line(self):
        """Test SQL comment injection detection."""
        query = "SELECT * FROM Users; -- DROP TABLE Users"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertFalse(is_safe)
    
    def test_comment_injection_multi_line(self):
        """Test multi-line comment injection detection."""
        query = "SELECT * FROM Users /* DROP TABLE Users */"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertFalse(is_safe)
    
    def test_multiple_statements_detection(self):
        """Test detection of multiple SQL statements."""
        query = "SELECT * FROM Users; INSERT INTO Users VALUES (1, 'John')"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertFalse(is_safe)
    
    def test_drop_injection_detection(self):
        """Test DROP injection detection."""
        query = "SELECT * FROM Users; DROP TABLE Users"
        is_safe, msg = SQLGuardrails.check_query_safety(query)
        self.assertFalse(is_safe)
    
    def test_sanitize_query_removes_comments(self):
        """Test SQL sanitization removes comments."""
        query = "SELECT * FROM Users -- malicious comment"
        sanitized = SQLGuardrails.sanitize_query(query)
        self.assertNotIn("--", sanitized)
        self.assertNotIn("malicious", sanitized)
    
    def test_sanitize_query_removes_multiline_comments(self):
        """Test sanitization removes multi-line comments."""
        query = "SELECT * FROM Users /* malicious comment */"
        sanitized = SQLGuardrails.sanitize_query(query)
        self.assertNotIn("/*", sanitized)
        self.assertNotIn("malicious", sanitized)
    
    def test_sanitize_query_removes_trailing_semicolon(self):
        """Test sanitization removes trailing semicolon."""
        query = "SELECT * FROM Users;"
        sanitized = SQLGuardrails.sanitize_query(query)
        self.assertFalse(sanitized.endswith(";"))
    
    def test_sanitize_query_preserves_content(self):
        """Test sanitization preserves main query content."""
        query = "SELECT * FROM Users WHERE age > 18 -- comment"
        sanitized = SQLGuardrails.sanitize_query(query)
        self.assertIn("SELECT", sanitized)
        self.assertIn("Users", sanitized)


class TestSQLExecutor(unittest.TestCase):
    """Test SQL database executor functions."""
    
    def setUp(self):
        """Create temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create a test table
        conn, cursor = get_database_connection(self.db_path)
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
            )
        """)
        cursor.execute("INSERT INTO users VALUES (1, 'Alice', 25)")
        cursor.execute("INSERT INTO users VALUES (2, 'Bob', 30)")
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up temporary database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_database_connection(self):
        """Test database connection establishment."""
        conn, cursor = get_database_connection(self.db_path)
        self.assertIsNotNone(conn)
        self.assertIsNotNone(cursor)
        conn.close()
    
    def test_execute_simple_query(self):
        """Test executing a simple SELECT query."""
        conn, cursor = get_database_connection(self.db_path)
        result = execute_query(cursor, "SELECT * FROM users")
        rows = result.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][1], 'Alice')
        conn.close()
    
    def test_execute_query_with_where(self):
        """Test executing query with WHERE clause."""
        conn, cursor = get_database_connection(self.db_path)
        result = execute_query(cursor, "SELECT * FROM users WHERE age > 25")
        rows = result.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 'Bob')
        conn.close()
    
    def test_execute_multiple_queries(self):
        """Test executing multiple queries."""
        conn, cursor = get_database_connection(self.db_path)
        queries = [
            "INSERT INTO users VALUES (3, 'Charlie', 35)",
            "INSERT INTO users VALUES (4, 'David', 28)"
        ]
        execute_queries(cursor, queries)
        commit_db_changes(conn)
        
        result = execute_query(cursor, "SELECT COUNT(*) FROM users")
        count = result.fetchone()[0]
        self.assertEqual(count, 4)
        conn.close()
    
    def test_close_connection(self):
        """Test closing database connection."""
        conn, cursor = get_database_connection(self.db_path)
        close_db_connection(conn)
        # Attempting to use closed connection should raise error
        with self.assertRaises(sqlite3.ProgrammingError):
            cursor.execute("SELECT * FROM users")


class TestSchemaIntrospector(unittest.TestCase):
    """Test database schema introspection functions."""
    
    def setUp(self):
        """Create temporary database with schema for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        conn, cursor = get_database_connection(self.db_path)
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount REAL
            )
        """)
        conn.commit()
        self.conn = conn
        self.cursor = cursor
    
    def tearDown(self):
        """Clean up temporary database."""
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_get_all_tables(self):
        """Test retrieving all table names."""
        tables = get_all_tables(self.cursor)
        self.assertIn('users', tables)
        self.assertIn('orders', tables)
        self.assertEqual(len(tables), 2)
    
    def test_get_table_schema(self):
        """Test retrieving table schema."""
        schema = get_table_schema(self.cursor, 'users')
        self.assertIn('CREATE TABLE', schema)
        self.assertIn('users', schema)
        self.assertIn('id', schema)
    
    def test_get_table_columns(self):
        """Test retrieving table column information."""
        columns = get_table_columns(self.cursor, 'users')
        self.assertEqual(len(columns), 3)
        
        col_names = [col['name'] for col in columns]
        self.assertIn('id', col_names)
        self.assertIn('name', col_names)
        self.assertIn('email', col_names)
    
    def test_get_table_columns_properties(self):
        """Test column properties are correctly retrieved."""
        columns = get_table_columns(self.cursor, 'users')
        
        # Find the 'name' column
        name_col = next(col for col in columns if col['name'] == 'name')
        self.assertEqual(name_col['type'], 'TEXT')
        self.assertTrue(name_col['notnull'])
    
    def test_get_database_schema(self):
        """Test retrieving complete database schema."""
        schema = get_database_schema(self.cursor)
        self.assertIn('CREATE TABLE users', schema)
        self.assertIn('CREATE TABLE orders', schema)
    
    def test_get_nonexistent_table_schema(self):
        """Test retrieving schema for non-existent table."""
        schema = get_table_schema(self.cursor, 'nonexistent')
        self.assertEqual(schema, "")


if __name__ == '__main__':
    unittest.main()
