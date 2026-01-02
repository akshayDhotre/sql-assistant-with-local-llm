"""
Evaluation dataset and metrics

This module provides dataset loading and evaluation metrics.
"""

import json
from typing import List, Dict, Any


def load_evaluation_dataset(filepath: str) -> List[Dict[str, Any]]:
    """
    Load evaluation dataset from JSON file.
    
    Args:
        filepath: Path to evaluation dataset JSON file
        
    Returns:
        List of test cases
    """
    try:
        with open(filepath, 'r') as f:
            dataset = json.load(f)
        return dataset
    except FileNotFoundError:
        print(f"Dataset file not found: {filepath}")
        return []


def save_evaluation_results(results: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save evaluation results to JSON file.
    
    Args:
        results: List of evaluation results
        filepath: Output filepath
    """
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)


def create_sample_dataset() -> List[Dict[str, Any]]:
    """
    Create sample evaluation dataset for testing.
    
    Returns:
        Sample dataset
    """
    return [
        {
            "id": 1,
            "question": "From students attendance find top 5 students with highest attendance and give me their marks in math.",
            "expected_query": "SELECT T2.Name, T1.Math FROM Marks AS T1 JOIN Students AS T2 ON T1.StudentID = T2.StudentID WHERE T2.Name IN (SELECT T4.Name FROM Attendance AS T3 JOIN Students AS T4 ON T3.StudentID = T4.StudentID ORDER BY T3.AttendancePercentage DESC LIMIT 5)",
            "expected_columns": ["Name", "Math"]
        },
        {
            "id": 2,
            "question": "Show me all students with their math marks.",
            "expected_query": "SELECT s.Name, m.Math FROM Students s JOIN Marks m ON s.StudentID = m.StudentID",
            "expected_columns": ["Name", "Math"]
        }
    ]
