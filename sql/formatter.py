"""
SQL formatting and result summary utilities

Author: Akshay Dhotre
"""

from typing import List, Dict, Any


def format_sql_result_summary(columns: List[str], rows: List[tuple], max_rows: int = 5) -> str:
    """
    Format database results into a natural language summary.
    
    Args:
        columns: Column names from the query
        rows: Result rows from the query
        max_rows: Maximum rows to include in summary
        
    Returns:
        Formatted summary string
    """
    if not rows:
        return "The query returned no results."
    
    num_rows = len(rows)
    displayed_rows = rows[:max_rows]
    
    # Create a text representation of results
    summary_lines = [f"Query returned {num_rows} row{'s' if num_rows != 1 else '}."]
    summary_lines.append(f"Columns: {', '.join(columns)}")
    summary_lines.append("\nResults:")
    
    for i, row in enumerate(displayed_rows, 1):
        row_str = " | ".join(str(val) for val in row)
        summary_lines.append(f"  {i}. {row_str}")
    
    if num_rows > max_rows:
        summary_lines.append(f"  ... and {num_rows - max_rows} more rows")
    
    return "\n".join(summary_lines)


def clean_sql_response(response: str) -> str:
    """
    Clean and extract SQL from LLM response.
    
    Args:
        response: Raw response from LLM
        
    Returns:
        Cleaned SQL query
    """
    sql = response.strip()
    
    # Remove markdown code blocks if present
    if sql.startswith("```"):
        lines = sql.split('\n')
        # Find first non-empty line after opening backticks
        start_idx = 1
        while start_idx < len(lines) and not lines[start_idx].strip():
            start_idx += 1
        # Find last non-empty line before closing backticks
        end_idx = len(lines) - 1
        while end_idx > start_idx and not lines[end_idx].strip():
            end_idx -= 1
        
        if end_idx > start_idx:
            sql = '\n'.join(lines[start_idx:end_idx])
    
    return sql.strip()


def generate_result_prompt(columns: List[str], rows: List[tuple], question: str, max_rows: int = 5) -> str:
    """
    Generate a prompt for LLM to summarize query results.
    
    Args:
        columns: Column names
        rows: Result rows
        question: Original user question
        max_rows: Maximum rows to include
        
    Returns:
        Prompt for LLM
    """
    num_rows = len(rows)
    displayed_rows = rows[:max_rows]
    
    rows_str = "\n".join([
        f"  Row {i}: {' | '.join(str(v) for v in row)}"
        for i, row in enumerate(displayed_rows, 1)
    ])
    
    if num_rows > max_rows:
        rows_str += f"\n  ... and {num_rows - max_rows} more rows"
    
    prompt = f"""Based on the user's question and the SQL query results, provide a brief natural language summary.

User Question: {question}

Column Names: {', '.join(columns)}

Query Results ({num_rows} total rows):
{rows_str}

Please provide a concise, human-readable summary of these results in 1-2 sentences."""
    
    return prompt
