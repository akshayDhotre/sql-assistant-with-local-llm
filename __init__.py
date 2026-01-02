"""
SQL Assistant with Local LLM

A modern SQL chatbot application that converts natural language to SQL queries
using locally-running LLM models with built-in security and validation.

Version: 1.0.0
Author: Akshay Dhotre
"""

__version__ = "1.0.0"
__author__ = "Akshay Dhotre"

# Import main components for easy access
from llm import get_llm_model, get_response_from_llm_model
from sql import (
    get_database_connection,
    execute_query,
    execute_queries,
    commit_db_changes,
    close_db_connection
)
from sql.validator import validate_query
from sql.schema_introspector import get_database_schema
from security.sql_guardrails import SQLGuardrails

__all__ = [
    "get_llm_model",
    "get_response_from_llm_model",
    "get_database_connection",
    "execute_query",
    "execute_queries",
    "commit_db_changes",
    "close_db_connection",
    "validate_query",
    "get_database_schema",
    "SQLGuardrails",
]
