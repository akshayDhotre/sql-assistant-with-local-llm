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
    print(f'****\n\nPrompt to LLM - \n {prompt}\n\n****')
    response = llm_model(prompt=prompt)
    print(f'****\n\nResponse from LLM - \n {response}\n\n****')
    return prompt, response


def get_result_summary(llm_model, analysis_prompt: str) -> str:
    """
    Generate AI-powered summary/insights for query results.
    
    Simple, focused function for result analysis - separate from SQL generation.
    
    Args:
        llm_model: Ollama client instance
        analysis_prompt: Pre-formatted analysis prompt with context
        
    Returns:
        Summary/insights text from LLM
    """
    print(f'****\n\nPrompt to LLM for Result Analysis - \n {analysis_prompt}\n\n****')
    response = llm_model(prompt=analysis_prompt)
    print(f'****\n\nResponse from LLM for Result Analysis - \n {response}\n\n****')
    return response
