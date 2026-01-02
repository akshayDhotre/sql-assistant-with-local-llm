"""
SQL module for database operations

This module handles database connections, schema introspection, query generation,
validation, and execution.
"""

from .executor import (
    get_database_connection,
    execute_query,
    execute_queries,
    commit_db_changes,
    close_db_connection
)

__all__ = [
    "get_database_connection",
    "execute_query",
    "execute_queries",
    "commit_db_changes",
    "close_db_connection"
]
