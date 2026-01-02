"""
Evaluation runner for SQL generation

This module runs evaluation tests on SQL generation.
"""

from typing import Dict, Any, List
import json
from ..sql.executor import get_database_connection, execute_query
from ..sql.validator import validate_query


def run_evaluation(
    db_path: str,
    dataset: List[Dict[str, Any]],
    llm_inference_fn
) -> List[Dict[str, Any]]:
    """
    Run evaluation on generated SQL queries.
    
    Args:
        db_path: Path to database file
        dataset: List of test cases
        llm_inference_fn: Function to generate SQL from question
        
    Returns:
        List of evaluation results
    """
    results = []
    connection, cursor = get_database_connection(db_path)
    
    for test_case in dataset:
        question = test_case.get("question", "")
        expected_query = test_case.get("expected_query", "")
        
        # Generate query using LLM
        try:
            generated_query = llm_inference_fn(question)
            
            # Validate query
            is_valid, validation_msg = validate_query(generated_query)
            
            # Execute query if valid
            execution_success = False
            error_msg = None
            
            if is_valid:
                try:
                    result = execute_query(cursor, generated_query)
                    execution_success = True
                except Exception as e:
                    error_msg = str(e)
            
            result = {
                "test_id": test_case.get("id"),
                "question": question,
                "generated_query": generated_query,
                "expected_query": expected_query,
                "is_valid": is_valid,
                "validation_msg": validation_msg,
                "execution_success": execution_success,
                "error": error_msg
            }
            
            results.append(result)
            
        except Exception as e:
            results.append({
                "test_id": test_case.get("id"),
                "question": question,
                "error": f"Generation failed: {str(e)}"
            })
    
    connection.close()
    return results


def print_evaluation_summary(results: List[Dict[str, Any]]) -> None:
    """
    Print summary of evaluation results.
    
    Args:
        results: Evaluation results
    """
    total = len(results)
    valid = sum(1 for r in results if r.get("is_valid", False))
    executed = sum(1 for r in results if r.get("execution_success", False))
    
    print(f"\nEvaluation Summary:")
    print(f"Total tests: {total}")
    print(f"Valid queries: {valid}/{total} ({100*valid/total:.1f}%)")
    print(f"Executed successfully: {executed}/{total} ({100*executed/total:.1f}%)")
