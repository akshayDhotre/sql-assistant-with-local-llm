"""
Application-wide logging configuration.

This module provides centralized logging infrastructure for the entire
SQL Assistant application, including evaluation, LLM inference, SQL execution,
and security operations.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class AppLogger:
    """Centralized application-wide logger (singleton pattern)."""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger (singleton pattern)."""
        self.log_dir = Path("app_logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def get_logger(self, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger with the given name.
        
        Args:
            name: Logger name (typically module name or __name__)
            log_file: Optional custom log file name
            
        Returns:
            Configured logger instance
        """
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (DEBUG level - more detailed)
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"app_{timestamp}.log"
        
        log_path = self.log_dir / log_file
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        self._loggers[name] = logger
        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an application logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger
    """
    logger_instance = AppLogger()
    return logger_instance.get_logger(name)


def get_evaluation_logger(name: str = "__main__") -> logging.Logger:
    """
    Get an evaluation logger instance (alias for backwards compatibility).
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger
    """
    return get_logger(name)


# Convenience functions for common logging tasks

def log_test_case_start(logger: logging.Logger, test_id: int, question: str):
    """Log the start of a test case evaluation."""
    logger.info(f"Starting evaluation of test case {test_id}")
    logger.debug(f"Question: {question}")


def log_test_case_success(logger: logging.Logger, test_id: int, model: str, 
                         execution_time: float = None, composite_score: float = None):
    """Log successful test case evaluation."""
    if execution_time is not None and composite_score is not None:
        logger.info(
            f"✓ Test {test_id} ({model}) PASSED - "
            f"Score: {composite_score:.4f}, Time: {execution_time:.3f}s"
        )
    else:
        logger.info(f"✓ Test {test_id} ({model}): PASSED - Score: {composite_score:.4f}")


def log_test_case_failure(logger: logging.Logger, test_id: int, model: str, 
                         error: str, error_type: str = "EXECUTION"):
    """Log failed test case evaluation."""
    logger.warning(
        f"✗ Test {test_id} ({model}) FAILED ({error_type}) - {error}"
    )


def log_query_generation(logger: logging.Logger, test_id: int, model: str, 
                        question: str = None, generated_query: str = None, 
                        gen_time: float = None):
    """Log generated SQL query."""
    if gen_time is not None:
        logger.debug(f"Test {test_id} ({model}) - Query generation: {gen_time:.3f}s")
    if question and generated_query:
        logger.debug(f"Test {test_id} - Generated query for {model}:")
        logger.debug(f"  Question: {question}")
        logger.debug(f"  Query: {generated_query}")


def log_query_validation(logger: logging.Logger, test_id: int, is_valid: bool = None, 
                        validation_msg: str = ""):
    """Log query validation result."""
    if is_valid is None:
        # Support simple validation logging
        logger.debug(f"Test {test_id} - Query validation check")
    elif is_valid:
        logger.debug(f"Test {test_id} - Query validation: PASSED")
    else:
        logger.warning(f"Test {test_id} - Query validation: FAILED - {validation_msg}")


def log_query_execution(logger: logging.Logger, test_id: int, success: bool = None, 
                       execution_time: float = None, error: str = ""):
    """Log query execution result."""
    if success is None:
        logger.debug(f"Test {test_id} - Query execution")
    elif success:
        if execution_time:
            logger.debug(f"Test {test_id} - Query execution: SUCCESS ({execution_time:.3f}s)")
        else:
            logger.debug(f"Test {test_id} - Query execution: SUCCESS")
    else:
        logger.warning(f"Test {test_id} - Query execution: FAILED - {error}")


def log_metrics_calculated(logger: logging.Logger, test_id: int = None, metrics: dict = None):
    """Log calculated metrics."""
    if test_id and metrics:
        logger.debug(f"Test {test_id} - Metrics calculated:")
        for metric_name, value in metrics.items():
            logger.debug(f"  {metric_name}: {value:.4f}")
    elif metrics:
        for metric_name, value in metrics.items():
            logger.debug(f"  {metric_name}: {value:.4f}")


def log_model_summary(logger: logging.Logger, model_name: str, summary: dict):
    """Log model evaluation summary."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Model Summary: {model_name}")
    logger.info(f"{'='*80}")
    logger.info(f"Total tests: {summary.get('total_tests', 0)}")
    logger.info(f"Valid queries: {summary.get('valid_queries', 0)}/{summary.get('total_tests', 0)} ({summary.get('valid_queries_pct', 0):.1f}%)")
    logger.info(f"Executed successfully: {summary.get('executed', 0)}/{summary.get('total_tests', 0)} ({summary.get('executed_pct', 0):.1f}%)")
    logger.info(f"Errors: {summary.get('errors', 0)} ({summary.get('error_pct', 0):.1f}%)")
    
    if summary.get('similarity_metrics'):
        logger.info("Similarity Metrics:")
        for metric, value in summary['similarity_metrics'].items():
            logger.info(f"  {metric}: {value:.4f}")
    
    logger.info(f"Composite Score: {summary.get('composite_score', 0):.4f}")


def log_model_comparison(logger: logging.Logger, comparison: dict):
    """Log model comparison results."""
    logger.info(f"\n{'='*80}")
    logger.info("Model Comparison Results")
    logger.info(f"{'='*80}")
    
    if comparison.get('best_models'):
        best = comparison['best_models']
        logger.info("Best Performing Models:")
        if best.get('composite_score'):
            logger.info(f"  Composite Score: {best['composite_score']['model']} ({best['composite_score']['score']:.4f})")
        if best.get('execution_rate'):
            logger.info(f"  Execution Rate: {best['execution_rate']['model']} ({best['execution_rate']['score']:.1f}%)")
        if best.get('validity_rate'):
            logger.info(f"  Validity Rate: {best['validity_rate']['model']} ({best['validity_rate']['score']:.1f}%)")


def log_evaluation_start(logger: logging.Logger, model_count: int = None, test_count: int = None):
    """Log start of evaluation run."""
    logger.info(f"\n{'='*80}")
    logger.info("Starting Evaluation Run")
    logger.info(f"{'='*80}")
    if model_count:
        logger.info(f"Models to evaluate: {model_count}")
    if test_count:
        logger.info(f"Test cases: {test_count}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def log_evaluation_complete(logger: logging.Logger, duration: float = None, 
                           report_files: dict = None):
    """Log completion of evaluation run."""
    logger.info(f"\n{'='*80}")
    logger.info("Evaluation Complete")
    logger.info(f"{'='*80}")
    if duration:
        logger.info(f"Duration: {duration:.2f}s")
    if report_files:
        logger.info("Reports generated:")
        for report_type, path in report_files.items():
            logger.info(f"  {report_type}: {path}")
    logger.info(f"Log file: app_logs/app_*.log")
