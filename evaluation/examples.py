#!/usr/bin/env python3
"""
Quick reference and examples for the enhanced evaluation system.

This file contains practical examples for common evaluation tasks.
"""

# ============================================================================
# Example 1: Run Multi-Model Evaluation
# ============================================================================

def example_multi_model_evaluation():
    """Evaluate multiple models and generate reports."""
    from evaluation.metrics import load_evaluation_dataset
    from evaluation.run_eval import run_multi_model_evaluation, print_model_comparison
    from evaluation.report_generator import EvaluationReportGenerator
    from llm.loader import get_llm_model
    from llm.inference import get_response_from_llm_model
    from sql.schema_introspector import get_database_schema
    import yaml
    
    # Load configuration
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    
    # Setup
    db_path = config["database"]["path"]
    db_schema = get_database_schema(db_path)
    dataset = load_evaluation_dataset("evaluation/dataset.json")
    
    # Define models to evaluate
    models = [
        {"name": "phi", "model_id": "phi"},
        {"name": "llama3", "model_id": "llama3:latest"},
    ]
    
    # Create inference function factory
    def get_inference_fn(model_config):
        def inference(question: str) -> str:
            llm = get_llm_model(model_name=model_config["model_id"])
            _, response = get_response_from_llm_model(llm, db_schema, question)
            return response
        return inference
    
    # Run evaluation
    results = run_multi_model_evaluation(
        db_path=db_path,
        dataset=dataset,
        models=models,
        get_inference_fn=get_inference_fn
    )
    
    # Print comparison
    print_model_comparison(results["comparison"])
    
    # Generate reports
    report_gen = EvaluationReportGenerator(output_dir="evaluation_reports")
    reports = report_gen.generate_all_reports(results)
    
    print(f"\nReports generated: {reports}")
    return results


# ============================================================================
# Example 2: Single Model with Metrics
# ============================================================================

def example_single_model_metrics():
    """Evaluate single model and calculate all metrics."""
    from evaluation.metrics import (
        load_evaluation_dataset,
        calculate_all_metrics,
        calculate_metrics_summary
    )
    from evaluation.run_eval import run_evaluation, print_evaluation_summary
    
    # Load dataset
    dataset = load_evaluation_dataset("evaluation/dataset.json")
    
    # Define inference function (dummy example)
    def my_inference_fn(question: str) -> str:
        return "SELECT * FROM Students"
    
    # Run evaluation
    results = run_evaluation(
        db_path="students_data_multi_table.db",
        dataset=dataset,
        llm_inference_fn=my_inference_fn,
        model_name="my_model",
        calculate_metrics=True
    )
    
    # Get summary
    summary = calculate_metrics_summary(results)
    print_evaluation_summary(summary)
    
    # Access individual metrics
    for result in results:
        metrics = result.get("similarity_metrics", {})
        print(f"Test {result['test_id']}:")
        print(f"  Composite Score: {result.get('composite_score', 0):.4f}")
        print(f"  BLEU Score: {metrics.get('bleu_score', 0):.4f}")
        print(f"  F1 Score: {metrics.get('f1_score', 0):.4f}")


# ============================================================================
# Example 3: Compare Specific Metrics
# ============================================================================

def example_compare_metrics():
    """Compare metrics between two queries."""
    from evaluation.metrics import (
        calculate_exact_match,
        calculate_token_match,
        calculate_bleu_score,
        calculate_f1_score,
        calculate_semantic_similarity,
        calculate_all_metrics,
        calculate_composite_score
    )
    
    generated = "SELECT Name, Age FROM Students WHERE Age > 18"
    expected = "SELECT Name, Age FROM Students WHERE Age > 20"
    
    # Calculate individual metrics
    print("Individual Metrics:")
    print(f"  Exact Match: {calculate_exact_match(generated, expected):.4f}")
    print(f"  Token Match: {calculate_token_match(generated, expected):.4f}")
    print(f"  BLEU Score: {calculate_bleu_score(generated, expected):.4f}")
    print(f"  F1 Score: {calculate_f1_score(generated, expected):.4f}")
    print(f"  Semantic Similarity: {calculate_semantic_similarity(generated, expected):.4f}")
    
    # Calculate all at once
    metrics = calculate_all_metrics(generated, expected)
    print(f"\nAll Metrics: {metrics}")
    
    # Calculate composite with custom weights
    weights = {
        "exact_match": 0.1,
        "token_match": 0.2,
        "bleu_score": 0.2,
        "f1_score": 0.25,
        "semantic_similarity": 0.25,
    }
    composite = calculate_composite_score(metrics, weights)
    print(f"Composite Score (custom weights): {composite:.4f}")


# ============================================================================
# Example 4: Generate Reports Only
# ============================================================================

def example_generate_reports():
    """Generate reports from existing evaluation data."""
    import json
    from evaluation.report_generator import EvaluationReportGenerator
    
    # Load evaluation data
    with open("evaluation_reports/report_20240115_120000.json") as f:
        evaluation_data = json.load(f)
    
    # Generate all report formats
    report_gen = EvaluationReportGenerator(output_dir="my_reports")
    reports = report_gen.generate_all_reports(evaluation_data)
    
    print("Generated reports:")
    for report_type, path in reports.items():
        print(f"  {report_type}: {path}")


# ============================================================================
# Example 5: Analyze Results with Custom Logic
# ============================================================================

def example_custom_analysis():
    """Perform custom analysis on evaluation results."""
    import json
    from evaluation.metrics import calculate_metrics_summary
    
    # Load results
    with open("evaluation_reports/report_20240115_120000.json") as f:
        data = json.load(f)
    
    # Analyze each model
    for model_name, results in data["all_results"].items():
        print(f"\n=== {model_name} ===")
        
        # Count results by status
        valid = sum(1 for r in results if r.get("is_valid"))
        executed = sum(1 for r in results if r.get("execution_success"))
        errors = sum(1 for r in results if "error" in r)
        
        print(f"Valid: {valid}, Executed: {executed}, Errors: {errors}")
        
        # Find best and worst cases
        best = max(
            (r for r in results if r.get("similarity_metrics")),
            key=lambda r: r.get("composite_score", 0),
            default=None
        )
        worst = min(
            (r for r in results if r.get("similarity_metrics")),
            key=lambda r: r.get("composite_score", 0),
            default=None
        )
        
        if best:
            print(f"Best: Test {best['test_id']} (Score: {best['composite_score']:.4f})")
        if worst:
            print(f"Worst: Test {worst['test_id']} (Score: {worst['composite_score']:.4f})")
        
        # Performance stats
        gen_times = [r.get("generation_time_sec", 0) for r in results]
        if gen_times:
            print(f"Generation Time: avg={sum(gen_times)/len(gen_times):.2f}s, max={max(gen_times):.2f}s")


# ============================================================================
# Example 6: Filter and Compare Subsets
# ============================================================================

def example_filter_and_compare():
    """Filter evaluation results and compare subsets."""
    import json
    
    # Load results
    with open("evaluation_reports/report_20240115_120000.json") as f:
        data = json.load(f)
    
    # Filter results for specific test IDs
    target_ids = [1, 2, 3, 5]
    
    for model_name, results in data["all_results"].items():
        print(f"\n{model_name} - Results for tests {target_ids}:")
        
        filtered = [r for r in results if r.get("test_id") in target_ids]
        
        for result in filtered:
            score = result.get("composite_score", 0)
            success = "✓" if result.get("execution_success") else "✗"
            print(f"  Test {result['test_id']}: {success} Score={score:.4f}")


# ============================================================================
# Example 7: Command-Line Usage
# ============================================================================

def example_cli_usage():
    """Examples of using the evaluation script from command line."""
    
    examples = [
        # Basic usage
        ("python -m evaluation.evaluate_models",
         "Run evaluation with default config"),
        
        # Specific models
        ("python -m evaluation.evaluate_models --models phi llama3",
         "Evaluate only phi and llama3 models"),
        
        # Custom paths
        ("python -m evaluation.evaluate_models --config my_config.yaml --dataset my_dataset.json",
         "Use custom configuration and dataset"),
        
        # Custom output
        ("python -m evaluation.evaluate_models --output /tmp/reports",
         "Save reports to /tmp/reports"),
        
        # Full custom setup
        ("python -m evaluation.evaluate_models "
         "--config custom.yaml "
         "--dataset data.json "
         "--output reports/ "
         "--models phi llama3 mistral "
         "--db /path/to/db.sqlite",
         "Full custom setup with all options"),
    ]
    
    for cmd, description in examples:
        print(f"{description}:")
        print(f"  $ {cmd}\n")


# ============================================================================
# Example 8: Integration with Tests
# ============================================================================

def example_test_integration():
    """Example of using evaluation in test suite."""
    
    test_code = '''
import pytest
from evaluation.run_eval import run_evaluation
from evaluation.metrics import calculate_metrics_summary

@pytest.fixture
def sql_generator():
    """Fixture providing SQL generator function."""
    def generate(question: str) -> str:
        # Your SQL generation logic here
        return "SELECT * FROM Students"
    return generate

def test_sql_generation_quality(sql_generator):
    """Test that SQL generation meets quality threshold."""
    from evaluation.metrics import load_evaluation_dataset
    
    dataset = load_evaluation_dataset("evaluation/dataset.json")
    results = run_evaluation(
        db_path="test.db",
        dataset=dataset,
        llm_inference_fn=sql_generator,
        model_name="test"
    )
    
    summary = calculate_metrics_summary(results)
    
    # Assert minimum quality thresholds
    assert summary["executed_pct"] >= 80, "Execution rate below 80%"
    assert summary["valid_queries_pct"] >= 90, "Validity rate below 90%"
    assert summary["composite_score"] >= 0.70, "Composite score below 0.70"

def test_execution_performance(sql_generator):
    """Test that SQL generation is performant."""
    from evaluation.metrics import load_evaluation_dataset
    
    dataset = load_evaluation_dataset("evaluation/dataset.json")
    results = run_evaluation(
        db_path="test.db",
        dataset=dataset,
        llm_inference_fn=sql_generator,
        model_name="test"
    )
    
    # Check performance
    avg_gen_time = sum(r.get("generation_time_sec", 0) for r in results) / len(results)
    assert avg_gen_time < 5.0, f"Generation too slow: {avg_gen_time}s average"
    '''
    
    print("Integration with pytest:\n")
    print(test_code)


# ============================================================================
# Run Examples
# ============================================================================

if __name__ == "__main__":
    import sys
    
    examples = {
        "1": ("Multi-model evaluation", example_multi_model_evaluation),
        "2": ("Single model metrics", example_single_model_metrics),
        "3": ("Compare metrics", example_compare_metrics),
        "4": ("Generate reports", example_generate_reports),
        "5": ("Custom analysis", example_custom_analysis),
        "6": ("Filter and compare", example_filter_and_compare),
        "7": ("CLI usage", example_cli_usage),
        "8": ("Test integration", example_test_integration),
    }
    
    print("\n" + "="*70)
    print("Evaluation System - Quick Reference Examples")
    print("="*70 + "\n")
    
    if len(sys.argv) > 1:
        example_key = sys.argv[1]
        if example_key in examples:
            title, func = examples[example_key]
            print(f"Running: {title}\n")
            print("-"*70 + "\n")
            func()
        else:
            print(f"Unknown example: {example_key}")
            print(f"Available: {', '.join(examples.keys())}")
    else:
        print("Available examples:\n")
        for key, (title, _) in examples.items():
            print(f"  {key}. {title}")
        
        print("\nUsage:")
        print("  python evaluation/examples.py <number>")
        print("\nExample:")
        print("  python evaluation/examples.py 1")
