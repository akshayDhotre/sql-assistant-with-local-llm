"""
Inference module for LLM-based SQL generation

This module handles generating SQL queries using Ollama LLM service.
"""

from .prompts import get_sql_generation_prompt


def get_response_from_llm_model(llm_model, table_schema: str, question: str) -> tuple:
    """
    Generate SQL query response from Ollama LLM based on natural language question.
    
    Args:
        llm_model: Ollama client instance
        table_schema: Database schema information
        question: Natural language question
        
    Returns:
        Tuple of (prompt, response) - the prompt sent and LLM's response
    """
    prompt = get_sql_generation_prompt(table_schema, question)
    print(f'Prompt to LLM - \n {prompt}')
    response = llm_model(prompt=prompt)
    return prompt, response
