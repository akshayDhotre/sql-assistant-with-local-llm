"""
Core application modules for SQL Assistant.
"""

from core.logging import (
    get_logger,
    get_evaluation_logger,
    AppLogger,
    log_test_case_start,
    log_test_case_success,
    log_test_case_failure,
    log_query_generation,
    log_query_validation,
    log_query_execution,
    log_metrics_calculated,
    log_model_summary,
    log_model_comparison,
    log_evaluation_start,
    log_evaluation_complete,
)

__all__ = [
    'get_logger',
    'get_evaluation_logger',
    'AppLogger',
    'log_test_case_start',
    'log_test_case_success',
    'log_test_case_failure',
    'log_query_generation',
    'log_query_validation',
    'log_query_execution',
    'log_metrics_calculated',
    'log_model_summary',
    'log_model_comparison',
    'log_evaluation_start',
    'log_evaluation_complete',
]
