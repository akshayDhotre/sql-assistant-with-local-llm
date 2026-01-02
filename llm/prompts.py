"""
Prompt templates for SQL generation

This module contains templated prompts for generating SQL queries from natural language.
"""


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

    Given the table structure from database, provide SQL query to question: `{question}`.
    
    SQL query:
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
