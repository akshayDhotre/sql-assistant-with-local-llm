"""
Unit tests for LLM inference and prompt modules

Author: Akshay Dhotre
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from llm.prompts import (
    get_sql_generation_prompt, 
    get_validation_prompt, 
    generate_result_prompt
)
from llm.inference import get_response_from_llm_model, get_result_summary


class TestPromptGeneration(unittest.TestCase):
    """Test prompt template generation."""
    
    def test_sql_generation_prompt_contains_schema(self):
        """Test that SQL generation prompt contains table schema."""
        schema = "CREATE TABLE users (id INT, name VARCHAR(100))"
        question = "Show all users"
        prompt = get_sql_generation_prompt(schema, question)
        
        self.assertIn(schema, prompt)
        self.assertIn(question, prompt)
    
    def test_sql_generation_prompt_contains_instructions(self):
        """Test that SQL generation prompt contains clear instructions."""
        schema = "CREATE TABLE users (id INT)"
        question = "Show all users"
        prompt = get_sql_generation_prompt(schema, question)
        
        self.assertIn("SELECT", prompt)
        self.assertIn("SQL", prompt)
        self.assertIn("single line", prompt.lower())
    
    def test_sql_generation_prompt_format(self):
        """Test that SQL generation prompt has proper structure."""
        schema = "CREATE TABLE users (id INT)"
        question = "How many users?"
        prompt = get_sql_generation_prompt(schema, question)
        
        # Should contain examples
        self.assertIn("Example", prompt)
        # Should have distinct sections
        self.assertIn("###", prompt)
    
    def test_validation_prompt_contains_query(self):
        """Test that validation prompt contains the query to check."""
        query = "SELECT * FROM users"
        schema = "CREATE TABLE users (id INT)"
        prompt = get_validation_prompt(query, schema)
        
        self.assertIn(query, prompt)
        self.assertIn(schema, prompt)
    
    def test_validation_prompt_mentions_safety(self):
        """Test that validation prompt mentions safety concerns."""
        query = "SELECT * FROM users"
        schema = "CREATE TABLE users (id INT)"
        prompt = get_validation_prompt(query, schema)
        
        prompt_lower = prompt.lower()
        self.assertTrue("safe" in prompt_lower or "valid" in prompt_lower)
    
    def test_result_prompt_with_single_row(self):
        """Test result analysis prompt with single row."""
        columns = ['id', 'name', 'age']
        rows = [(1, 'Alice', 25)]
        question = "Who is the youngest user?"
        
        prompt = generate_result_prompt(columns, rows, question)
        
        self.assertIn('Alice', prompt)
        self.assertIn('25', prompt)
        self.assertIn(question, prompt)
    
    def test_result_prompt_with_multiple_rows(self):
        """Test result analysis prompt with multiple rows."""
        columns = ['id', 'name']
        rows = [(1, 'Alice'), (2, 'Bob'), (3, 'Charlie')]
        question = "List all users"
        
        prompt = generate_result_prompt(columns, rows, question)
        
        self.assertIn('Alice', prompt)
        self.assertIn('Bob', prompt)
        self.assertIn(question, prompt)
    
    def test_result_prompt_with_many_rows(self):
        """Test result analysis prompt truncates large datasets."""
        columns = ['id']
        rows = [(i,) for i in range(100)]
        question = "Show all IDs"
        
        prompt = generate_result_prompt(columns, rows, question)
        
        # Should mention total count
        self.assertIn('100', prompt)
        # Should indicate there are more rows
        self.assertIn('...', prompt)
    
    def test_result_prompt_format(self):
        """Test result analysis prompt proper formatting."""
        columns = ['name', 'score']
        rows = [('Alice', 95), ('Bob', 87)]
        question = "Top scores?"
        
        prompt = generate_result_prompt(columns, rows, question)
        
        # Should have column information
        self.assertIn('name', prompt)
        self.assertIn('score', prompt)
        # Should show result count
        self.assertIn('Results:', prompt.replace('result', 'Result').replace('Number', 'number'))


class TestLLMInference(unittest.TestCase):
    """Test LLM inference functions."""
    
    def test_get_response_from_llm_model_calls_llm(self):
        """Test that inference function calls the LLM model."""
        # Mock the LLM model
        mock_llm = Mock()
        mock_llm.return_value = "SELECT * FROM users"
        
        schema = "CREATE TABLE users (id INT, name VARCHAR(100))"
        question = "Show all users"
        
        prompt, response = get_response_from_llm_model(mock_llm, schema, question)
        
        # Verify LLM was called
        mock_llm.assert_called_once()
        # Verify response was returned
        self.assertEqual(response, "SELECT * FROM users")
    
    def test_get_response_from_llm_model_returns_tuple(self):
        """Test that inference returns both prompt and response."""
        mock_llm = Mock()
        mock_llm.return_value = "SELECT * FROM users"
        
        schema = "CREATE TABLE users (id INT)"
        question = "Show all users"
        
        result = get_response_from_llm_model(mock_llm, schema, question)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        prompt, response = result
        self.assertIsInstance(prompt, str)
        self.assertIsInstance(response, str)
    
    def test_get_response_from_llm_model_prompt_content(self):
        """Test that the prompt passed to LLM contains required info."""
        mock_llm = Mock()
        mock_llm.return_value = "SELECT * FROM users"
        
        schema = "CREATE TABLE users (id INT)"
        question = "Show all users"
        
        prompt, _ = get_response_from_llm_model(mock_llm, schema, question)
        
        # Prompt should contain both schema and question
        self.assertIn(schema, prompt)
        self.assertIn(question, prompt)
    
    def test_get_result_summary_calls_llm(self):
        """Test that result summary function calls LLM."""
        mock_llm = Mock()
        mock_llm.return_value = "The results show a high correlation"
        
        analysis_prompt = "Analyze these results: ..."
        
        summary = get_result_summary(mock_llm, analysis_prompt)
        
        mock_llm.assert_called_once()
        self.assertEqual(summary, "The results show a high correlation")
    
    def test_get_result_summary_with_different_prompts(self):
        """Test result summary with various analysis prompts."""
        mock_llm = Mock()
        mock_llm.return_value = "Summary"
        
        test_prompts = [
            "Analyze sales data...",
            "What patterns do you see...",
            "Summarize the findings..."
        ]
        
        for test_prompt in test_prompts:
            summary = get_result_summary(mock_llm, test_prompt)
            self.assertEqual(summary, "Summary")


class TestPromptEdgeCases(unittest.TestCase):
    """Test prompt generation with edge cases."""
    
    def test_sql_generation_with_complex_schema(self):
        """Test prompt generation with complex schema."""
        schema = """
        CREATE TABLE orders (
            id INT PRIMARY KEY,
            user_id INT FOREIGN KEY,
            amount DECIMAL(10,2),
            created_at TIMESTAMP
        );
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        );
        """
        question = "Total sales by user?"
        
        prompt = get_sql_generation_prompt(schema, question)
        
        self.assertIn(schema, prompt)
        self.assertIn(question, prompt)
    
    def test_sql_generation_with_special_characters_in_question(self):
        """Test prompt with special characters in question."""
        schema = "CREATE TABLE users (id INT)"
        question = "Find users with 'admin' role and age > 21?"
        
        prompt = get_sql_generation_prompt(schema, question)
        
        self.assertIn(question, prompt)
    
    def test_result_prompt_with_empty_rows(self):
        """Test result prompt with no results."""
        columns = ['id', 'name']
        rows = []
        question = "Show users"
        
        prompt = generate_result_prompt(columns, rows, question)
        
        self.assertIn('0', prompt)  # Should show 0 results
        self.assertIn(question, prompt)
    
    def test_result_prompt_with_none_values(self):
        """Test result prompt with NULL values."""
        columns = ['id', 'name', 'phone']
        rows = [(1, 'Alice', '555-1234'), (2, 'Bob', None)]
        question = "Show contacts"
        
        prompt = generate_result_prompt(columns, rows, question)
        
        self.assertIn('Alice', prompt)
        self.assertIn('Bob', prompt)
    
    def test_validation_prompt_with_invalid_query(self):
        """Test validation prompt with intentionally bad query."""
        query = "SELCT * FORM users"  # Typos
        schema = "CREATE TABLE users (id INT)"
        
        prompt = get_validation_prompt(query, schema)
        
        self.assertIn(query, prompt)


if __name__ == '__main__':
    unittest.main()
