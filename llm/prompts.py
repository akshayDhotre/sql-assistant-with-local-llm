"""
Prompt templates for SQL generation

This module contains templated prompts for generating SQL queries from natural language.
"""

from typing import List


def get_sql_generation_prompt(table_schema: str, question: str) -> str:
    """
    Generate a prompt for SQL query generation.
    
    Args:
        table_schema: Database schema information as string
        question: Natural language question from user
        
    Returns:
        Formatted prompt for LLM
    """
    prompt = f'''
    You are a professional SQL developer. Understand the question and return the most suitable query.
    Using valid SQLite syntax, answer the question for the table information provided below.

    ### Database Tables Schema
    `{table_schema}`

    Given the database table structure, provide an SQL query that answers the question: `{question}`.
    Your response should start with SELECT and be a single line SQL query without any explanations.

    ### Example 1:
    Question: Show all employees in the 'Sales' department.
    Your Answer: SELECT * FROM employees WHERE department = 'Sales';

    ### Example 2:
    Question: How many orders were placed in 2023?
    Your Answer: SELECT COUNT(*) FROM orders WHERE strftime('%Y', order_date) = '2023';

    Now generate the SQL…
    '''
    return prompt


def get_validation_prompt(sql_query: str, table_schema: str) -> str:
    """
    Generate a prompt for SQL query validation.
    
    Args:
        sql_query: SQL query to validate
        table_schema: Database schema information
        
    Returns:
        Formatted validation prompt
    """
    prompt = f'''
    You are a SQL expert. Review the following SQL query for correctness and safety.
    
    ### Database Schema
    `{table_schema}`
    
    ### Query to Validate
    {sql_query}
    
    Is this query valid and safe? Respond with: VALID or INVALID [reason]
    '''
    return prompt


def generate_result_prompt(columns: List[str], rows: List[tuple], question: str) -> str:
    """
    Generate a prompt for LLM to analyze and summarize query results.
    
    Args:
        columns: Column names from the query
        rows: Result rows from the query
        question: Original user question
        
    Returns:
        Prompt for LLM to generate insights
    """
    num_rows = len(rows)
    rows_preview = rows[:10]  # Show up to 10 rows for context
    
    # Format sample data with column names
    sample_data = "\n".join([
        f"  Row {i}: " + " | ".join(f"{col}: {val}" for col, val in zip(columns, row))
        for i, row in enumerate(rows_preview, 1)
    ])
    
    # Add indicator if there are more rows
    if num_rows > 10:
        sample_data += f"\n  ...\nTotal: {num_rows} results"
    
    prompt = f"""Analyze these database query results and provide insights:

    Original Question: {question}
    Column Names: {', '.join(columns)}
    Number of Results: {num_rows}

    Data (first {min(num_rows, 10)} rows):
    {sample_data}

    Provide concise insights:
    1. Key findings/patterns (2-3 sentences)
    2. Notable observations
    3. Brief summary

    Response should be well formatted and pointwise to show on UI
    Be direct and avoid obvious statements."""
    
    return prompt
