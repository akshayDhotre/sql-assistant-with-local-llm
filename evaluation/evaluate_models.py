"""
Comprehensive evaluation script for multi-model SQL generation testing.

This script evaluates SQL generation across multiple LLM models and generates reports.

Usage:
    python -m evaluation.evaluate_models
    python -m evaluation.evaluate_models --config config.yaml
    python -m evaluation.evaluate_models --models phi llama3 --output reports/
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List, Callable
import time

# Adjust path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.loader import get_llm_model
from llm.inference import get_response_from_llm_model
from sql.executor import get_database_connection
from sql.schema_introspector import get_database_schema
from evaluation.metrics import load_evaluation_dataset
from evaluation.run_eval import run_multi_model_evaluation, print_model_comparison
from evaluation.report_generator import EvaluationReportGenerator
from core.logging import (
    get_evaluation_logger,
    log_evaluation_start,
    log_evaluation_complete,
)


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}


def get_inference_function(
    model_config: Dict[str, Any],
    db_schema: str,
    config: Dict[str, Any],
    logger=None
) -> Callable:
    """
    Create an inference function for a specific model.
    
    Args:
        model_config: Model configuration dictionary
        db_schema: Database schema string
        config: Global configuration
        logger: Optional logger instance
        
    Returns:
        Inference function
    """
    def inference_fn(question: str) -> str:
        """Generate SQL query from question."""
        try:
            llm_config = config.get("llm", {})
            base_url = llm_config.get("base_url", "http://localhost:11434")
            model_id = model_config.get("model_id", "phi")
            
            if logger:
                logger.debug(f"Loading model: {model_id}")
            
            # Load the LLM model
            llm_model = get_llm_model(ollama_base_url=base_url, model_name=model_id)
            
            if logger:
                logger.debug(f"Model {model_id} loaded successfully")
            
            # Generate SQL query
            _, response = get_response_from_llm_model(
                llm_model,
                table_schema=db_schema,
                question=question
            )
            
            if logger:
                logger.debug(f"Generated response from {model_id}: {response[:100]}...")
            
            return response
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if logger:
                logger.error(f"Model inference failed: {e}", exc_info=True)
            return error_msg
    
    return inference_fn


def main():
    """Main evaluation function."""
    # Initialize logger
    logger = get_evaluation_logger(__name__)
    
    parser = argparse.ArgumentParser(
        description="Evaluate SQL generation across multiple LLM models"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="evaluation/dataset.json",
        help="Path to evaluation dataset"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_reports",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=None,
        help="Specific models to evaluate (overrides config)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Database path (overrides config)"
    )
    
    args = parser.parse_args()
    
    # Log start
    logger.info("\n" + "="*80)
    logger.info("SQL Generation Multi-Model Evaluation")
    logger.info("="*80 + "\n")
    
    # Load configuration
    logger.info(f"Loading configuration from: {args.config}")
    config = load_config(args.config)
    
    if not config:
        logger.error("Could not load configuration")
        return 1
    logger.debug(f"Configuration loaded successfully")
    
    # Get database path
    db_path = args.db or config.get("database", {}).get("path", "students_data_multi_table.db")
    logger.info(f"Using database: {db_path}")
    
    # Get database schema
    logger.info("Introspecting database schema...")
    try:
        connection, cursor = get_database_connection(db_path)
        db_schema = get_database_schema(cursor)
        connection.close()
        logger.info(f"✓ Schema retrieved: {len(db_schema)} characters")
        logger.debug(f"Schema preview: {db_schema[:200]}...")
    except Exception as e:
        logger.error(f"Could not retrieve schema: {e}", exc_info=True)
        return 1
    
    # Load evaluation dataset
    logger.info(f"Loading evaluation dataset from: {args.dataset}")
    dataset = load_evaluation_dataset(args.dataset)
    
    if not dataset:
        logger.error(f"No dataset loaded from {args.dataset}")
        return 1
    
    logger.info(f"✓ Loaded {len(dataset)} test cases")
    for test_case in dataset:
        logger.debug(f"  Test {test_case.get('id')}: {test_case.get('question')[:80]}...")
    
    # Prepare models to evaluate
    models_to_eval = []
    
    if args.models:
        # Use command-line specified models
        logger.info(f"Using command-line specified models: {args.models}")
        for model_name in args.models:
            models_to_eval.append({
                "name": model_name,
                "model_id": model_name,
            })
    else:
        # Use models from config
        eval_models = config.get("llm", {}).get("evaluation_models", [])
        
        for model_config in eval_models:
            if model_config.get("enabled", False):
                models_to_eval.append(model_config)
    
    if not models_to_eval:
        logger.error("No models configured for evaluation")
        logger.error("Enable models in config.yaml or use --models argument")
        return 1
    
    logger.info(f"✓ Models to evaluate: {[m.get('name') for m in models_to_eval]}")
    
    # Create inference function factory
    def get_inference_fn(model_config: Dict[str, Any]) -> Callable:
        return get_inference_function(model_config, db_schema, config, logger)
    
    # Run multi-model evaluation
    logger.info("\n" + "="*80)
    logger.info("Starting evaluation...")
    logger.info("="*80)
    
    start_time = time.time()
    log_evaluation_start(logger, len(models_to_eval), len(dataset))
    
    try:
        evaluation_results = run_multi_model_evaluation(
            db_path=db_path,
            dataset=dataset,
            models=models_to_eval,
            get_inference_fn=get_inference_fn,
            logger=logger
        )
    except Exception as e:
        logger.error(f"Error during evaluation: {e}", exc_info=True)
        return 1
    
    # Print comparison
    logger.info("")
    print_model_comparison(evaluation_results.get("comparison", {}))
    
    # Generate reports
    logger.info("\n" + "="*80)
    logger.info("Generating reports...")
    logger.info("="*80 + "\n")
    
    report_gen = EvaluationReportGenerator(output_dir=args.output, logger=logger)
    
    try:
        report_paths = report_gen.generate_all_reports(evaluation_results)
        
        logger.info(f"✓ Reports generated in: {args.output}/")
        for report_type, path in report_paths.items():
            logger.info(f"  - {report_type}: {path}")
    
    except Exception as e:
        logger.error(f"Error generating reports: {e}", exc_info=True)
        return 1
    
    # Log completion
    duration = time.time() - start_time
    log_evaluation_complete(logger, duration, report_paths)
    
    logger.info("\n" + "="*80)
    logger.info("✓ Evaluation completed successfully!")
    logger.info("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
