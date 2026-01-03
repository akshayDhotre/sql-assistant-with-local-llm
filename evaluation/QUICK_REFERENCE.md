# Evaluation System - Quick Reference

## Quick Start (30 seconds)

```bash
# 1. Enable models in config.yaml (set enabled: true)
# 2. Run evaluation
python -m evaluation.evaluate_models

# 3. View results
cat evaluation_reports/report_*.md
```

## Command-Line Examples

```bash
# Default evaluation
python -m evaluation.evaluate_models

# Custom models
python -m evaluation.evaluate_models --models phi llama3 mistral

# Custom output directory
python -m evaluation.evaluate_models --output my_reports/

# Combine options
python -m evaluation.evaluate_models --models phi llama3 --output reports/
```

## Python API Quick Use

### Run Multi-Model Evaluation
```python
from evaluation.run_eval import run_multi_model_evaluation
from evaluation.report_generator import EvaluationReportGenerator

results = run_multi_model_evaluation(
    db_path="students_data_multi_table.db",
    dataset=test_cases,
    models=models,
    get_inference_fn=inference_factory
)

# Generate reports
gen = EvaluationReportGenerator()
gen.generate_all_reports(results)
```

### Calculate Metrics
```python
from evaluation.metrics import calculate_all_metrics

metrics = calculate_all_metrics(
    generated_query="SELECT Name FROM Students",
    expected_query="SELECT Name, Age FROM Students"
)
# Returns: {
#     "exact_match": 0.0,
#     "token_match": 0.8,
#     "bleu_score": 0.65,
#     "f1_score": 0.73,
#     "semantic_similarity": 0.85
# }
```

### Get Summary Statistics
```python
from evaluation.metrics import calculate_metrics_summary

summary = calculate_metrics_summary(results)
print(f"Composite Score: {summary['composite_score']:.4f}")
print(f"Execution Rate: {summary['executed_pct']:.1f}%")
```

## Configuration

### Enable/Disable Models
In `config.yaml`:
```yaml
llm:
  evaluation_models:
    - name: "phi"
      enabled: true      # Enable this model
    - name: "llama3"
      enabled: true
    - name: "mistral"
      enabled: false     # Disable this model
```

## Metrics Cheat Sheet

| Metric | Best | Good | Fair | Poor |
|--------|------|------|------|------|
| **Exact Match** | 1.0 | 0.5+ | 0.3+ | <0.3 |
| **Token Match** | 1.0 | 0.8+ | 0.6+ | <0.6 |
| **BLEU Score** | 1.0 | 0.8+ | 0.6+ | <0.6 |
| **F1 Score** | 1.0 | 0.8+ | 0.6+ | <0.6 |
| **Semantic Sim** | 1.0 | 0.8+ | 0.6+ | <0.6 |
| **Composite** | 1.0 | 0.75+ | 0.5+ | <0.5 |

## Report Files Generated

```
evaluation_reports/
├── report_20240115_120000.json    # Raw data
├── report_20240115_120000.md      # Formatted report
└── results_20240115_120000.csv    # Spreadsheet
```

**JSON** - All data, no formatting  
**Markdown** - Human-readable with analysis  
**CSV** - Data for Excel/Sheets

## Output File Example

### JSON Structure
```json
{
  "all_results": {
    "phi": [
      {
        "test_id": 1,
        "question": "...",
        "generated_query": "...",
        "execution_success": true,
        "similarity_metrics": {
          "exact_match": 1.0,
          "bleu_score": 0.95,
          ...
        },
        "composite_score": 0.92
      }
    ]
  },
  "model_summaries": {
    "phi": {
      "composite_score": 0.85,
      "executed_pct": 95.0,
      "valid_queries_pct": 98.0
    }
  },
  "comparison": {
    "best_models": {
      "composite_score": {"model": "phi", "score": 0.85}
    }
  }
}
```

## Common Tasks

### Evaluate New Model
```yaml
# config.yaml
llm:
  evaluation_models:
    - name: "my_model"
      model_id: "ollama_model_name"
      enabled: true
```
Then: `python -m evaluation.evaluate_models`

### Compare Two Models
```bash
python -m evaluation.evaluate_models --models phi llama3
```

### Save to Specific Location
```bash
python -m evaluation.evaluate_models --output ./my_results/
```

### Get Best Model
```python
from evaluation.run_eval import run_multi_model_evaluation

results = run_multi_model_evaluation(...)
best = results["comparison"]["best_models"]["composite_score"]
print(f"Best: {best['model']} with score {best['score']:.4f}")
```

### Create Custom Report
```python
from evaluation.report_generator import EvaluationReportGenerator
import json

# Load your data
with open("report.json") as f:
    data = json.load(f)

# Generate formats
gen = EvaluationReportGenerator(output_dir="custom/")
gen.generate_markdown_report(data, "my_report.md")
gen.generate_csv_report(data, "data.csv")
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No models found | Set `enabled: true` in config.yaml |
| Database not found | Check `database.path` in config.yaml |
| Ollama not running | Start: `ollama serve` |
| Model not found | Pull: `ollama pull model_name` |
| Out of memory | Use smaller model or reduce batch |
| Import errors | Ensure dependencies installed |

## Performance Tips

- **Faster** - Use `phi` model (smaller)
- **Better** - Use `llama3` model (larger)
- **Balance** - Use `mistral` model (medium)
- Start with **5-10 test cases** for quick feedback
- Run full evaluation **after major changes**

## File Locations

| File | Purpose |
|------|---------|
| `evaluation/metrics.py` | Metric calculations |
| `evaluation/run_eval.py` | Evaluation engine |
| `evaluation/report_generator.py` | Report generation |
| `evaluation/evaluate_models.py` | CLI interface |
| `evaluation/dataset.json` | Test cases |
| `config.yaml` | Configuration |
| `evaluation_reports/` | Generated reports |

## Next: Advanced Usage

- See [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md) for full API
- See [examples.py](examples.py) for code samples
- Check [EVALUATION_IMPROVEMENTS.md](../EVALUATION_IMPROVEMENTS.md) for changes

---

**Quick Support:**
```bash
python evaluation/examples.py 1    # Run example 1
python evaluation/examples.py 7    # View CLI examples
```
