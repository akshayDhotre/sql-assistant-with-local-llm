# Enhanced Evaluation System

This directory contains an improved evaluation framework for SQL generation with multiple LLM models.

## Overview

The evaluation system now includes:

1. **Advanced Metrics** - Multiple similarity and correctness metrics
2. **Multi-Model Support** - Evaluate and compare multiple LLM models
3. **Comprehensive Reports** - Generate detailed evaluation reports in multiple formats
4. **Performance Tracking** - Monitor query generation and execution times

## Components

### 1. Metrics Module (`metrics.py`)

Provides evaluation metrics for comparing generated SQL queries:

#### Similarity Metrics

- **Exact Match** - Binary score (1.0 if queries are identical, 0.0 otherwise)
- **Token Match** - Percentage of matching SQL tokens
- **BLEU Score** - N-gram overlap metric (0.0 - 1.0)
- **F1 Score** - Harmonic mean of precision and recall based on tokens
- **Semantic Similarity** - Similarity based on SQL keywords and operations

#### SQL Correctness

- **Validity Score** - Based on syntax validation
- **Execution Score** - Based on successful query execution
- **Composite Score** - Weighted combination of all metrics

#### Functions

```python
# Load and save data
load_evaluation_dataset(filepath)
save_evaluation_results(results, filepath)

# Individual metrics
calculate_exact_match(generated_query, expected_query)
calculate_token_match(generated_query, expected_query)
calculate_bleu_score(generated_query, expected_query)
calculate_f1_score(generated_query, expected_query)
calculate_semantic_similarity(generated_query, expected_query)

# Aggregate functions
calculate_all_metrics(generated_query, expected_query)
calculate_metrics_summary(results)
```

### 2. Evaluation Runner (`run_eval.py`)

Executes evaluation tests with detailed result tracking:

#### Functions

```python
# Single model evaluation
run_evaluation(db_path, dataset, llm_inference_fn, model_name, calculate_metrics)

# Multi-model evaluation
run_multi_model_evaluation(db_path, dataset, models, get_inference_fn)

# Reporting
print_evaluation_summary(summary)
print_model_comparison(comparison)
```

#### Result Structure

Each evaluation result includes:
- Query generation and validation results
- Execution success/failure
- All similarity metrics
- Performance timings
- Composite scores

### 3. Report Generator (`report_generator.py`)

Generates comprehensive evaluation reports:

#### Supported Formats

- **JSON** - Raw data for further processing
- **Markdown** - Human-readable report with analysis
- **CSV** - Tabular format for spreadsheets

#### Report Contents

- Executive summary with model comparison
- Best performing models by metric
- Detailed results for each model
- Sample test cases with metrics
- Recommendations based on results

#### Usage

```python
from evaluation.report_generator import EvaluationReportGenerator

gen = EvaluationReportGenerator(output_dir="reports/")

# Generate individual reports
gen.generate_json_report(evaluation_data)
gen.generate_markdown_report(evaluation_data)
gen.generate_csv_report(evaluation_data)

# Generate all formats at once
reports = gen.generate_all_reports(evaluation_data)
```

### 4. Evaluation Script (`evaluate_models.py`)

Complete evaluation pipeline with CLI:

```bash
# Run with default configuration
python -m evaluation.evaluate_models

# Use specific models
python -m evaluation.evaluate_models --models phi llama3 mistral

# Custom paths
python -m evaluation.evaluate_models \
  --config custom_config.yaml \
  --dataset custom_dataset.json \
  --output custom_reports/ \
  --db path/to/database.db
```

#### Command-Line Options

- `--config` - Configuration file path (default: config.yaml)
- `--dataset` - Evaluation dataset path (default: evaluation/dataset.json)
- `--output` - Output directory for reports (default: evaluation_reports/)
- `--models` - Specific models to evaluate (overrides config)
- `--db` - Database path (overrides config)

## Configuration

Edit `config.yaml` to configure models for evaluation:

```yaml
llm:
  base_url: "http://localhost:11434"
  evaluation_models:
    - name: "phi"
      model_id: "phi"
      enabled: true
      description: "Phi model - lightweight and fast"
    
    - name: "llama3"
      model_id: "llama3:latest"
      enabled: true
      description: "Llama 3 - most capable model"
    
    - name: "mistral"
      model_id: "mistral"
      enabled: false
      description: "Mistral - good balance"
```

Enable/disable models by setting `enabled: true/false`.

## Usage Examples

### Basic Multi-Model Evaluation

```python
from evaluation.metrics import load_evaluation_dataset
from evaluation.run_eval import run_multi_model_evaluation

# Load test cases
dataset = load_evaluation_dataset("evaluation/dataset.json")

# Define models
models = [
    {"name": "phi", "model_id": "phi"},
    {"name": "llama3", "model_id": "llama3:latest"},
]

# Define inference function factory
def get_inference_fn(model_config):
    # Return a function that generates SQL for this model
    pass

# Run evaluation
results = run_multi_model_evaluation(
    db_path="students_data_multi_table.db",
    dataset=dataset,
    models=models,
    get_inference_fn=get_inference_fn
)

# Print comparison
from evaluation.run_eval import print_model_comparison
print_model_comparison(results["comparison"])
```

### Generate Reports

```python
from evaluation.report_generator import EvaluationReportGenerator

gen = EvaluationReportGenerator(output_dir="reports/")
reports = gen.generate_all_reports(evaluation_data)

print(f"Reports saved to: {reports}")
```

### Analyze Single Model

```python
from evaluation.metrics import calculate_all_metrics, calculate_metrics_summary

# Calculate metrics for one test
metrics = calculate_all_metrics(
    generated_query="SELECT * FROM Students",
    expected_query="SELECT Name, Age FROM Students"
)

# Calculate summary for multiple tests
summary = calculate_metrics_summary(results)
print(f"Composite Score: {summary['composite_score']:.4f}")
print(f"Execution Rate: {summary['executed_pct']:.1f}%")
```

## Evaluation Dataset

The evaluation dataset is a JSON file with test cases:

```json
[
    {
        "id": 1,
        "question": "Natural language question",
        "expected_query": "SELECT ...",
        "expected_columns": ["col1", "col2"]
    },
    ...
]
```

Create additional datasets for specific domains or query types.

## Understanding Metrics

### Exact Match (0.0 - 1.0)
- **1.0**: Generated query is identical to expected (after normalization)
- **0.0**: Queries differ

**Use case**: Strict correctness checking

### Token Match (0.0 - 1.0)
- **1.0**: All expected tokens present in generated query
- **0.0**: No matching tokens

**Use case**: Identifying missing components

### BLEU Score (0.0 - 1.0)
- **1.0**: Perfect n-gram overlap
- **0.5**: ~50% n-gram overlap
- **0.0**: No n-gram overlap

**Use case**: Evaluating phrase-level similarity

### F1 Score (0.0 - 1.0)
- **1.0**: Perfect precision and recall
- **0.5**: Balanced but incomplete match
- **0.0**: No overlap

**Use case**: Balanced evaluation of coverage vs correctness

### Semantic Similarity (0.0 - 1.0)
- **1.0**: Same SQL keywords and operations
- **0.5**: Partial keyword overlap
- **0.0**: Different operations

**Use case**: Structural correctness despite syntax differences

### Composite Score
Weighted average of all metrics (default: equal weights).

## Report Examples

### Summary Statistics
```
Total tests: 20
Valid queries: 18/20 (90.0%)
Executed successfully: 16/20 (80.0%)
Errors: 2 (10.0%)
```

### Model Comparison
```
Best Composite Score: llama3 (0.8234)
Best Execution Rate: phi (95.0%)
Best Validity Rate: mistral (92.5%)
```

### Detailed Metrics
```
Model: llama3
- Exact Match: 0.4500
- Token Match: 0.8200
- BLEU Score: 0.7100
- F1 Score: 0.7800
- Semantic Similarity: 0.8500
- Composite Score: 0.7220
```

## Performance Metrics

Each evaluation result includes:
- `generation_time_sec` - Time to generate SQL (seconds)
- `execution_time_sec` - Time to execute query (seconds)
- `result_rows` - Number of rows returned

Use these to monitor model efficiency.

## Troubleshooting

### No models enabled
**Error**: "No models configured for evaluation"  
**Solution**: Set `enabled: true` in config.yaml for at least one model

### Database connection failed
**Error**: "Could not retrieve schema"  
**Solution**: Verify database path in config.yaml and that database file exists

### Model not found
**Error**: "Model not found in Ollama"  
**Solution**: Pull the model first: `ollama pull <model_name>`

### Out of memory
**Error**: "CUDA out of memory" or similar  
**Solution**: Use smaller models or reduce batch size

## Best Practices

1. **Start Small** - Test with 5-10 test cases before full evaluation
2. **Mix Complexities** - Include simple and complex queries
3. **Document Expectations** - Ensure expected_query is correct
4. **Regular Benchmarks** - Run evaluations after model or prompt changes
5. **Compare Baselines** - Always evaluate multiple models for comparison
6. **Review Failures** - Analyze failed cases to improve prompts
7. **Archive Reports** - Keep historical reports for trend analysis

## Contributing

To add new metrics:

1. Add metric function to `metrics.py`
2. Update `calculate_all_metrics()` to include new metric
3. Update report generator to display new metric
4. Document metric in README

## See Also

- [Evaluation Dataset Guide](dataset.json)
- [Configuration Guide](../config.yaml)
- [Main Evaluation Directory](../evaluation/)
