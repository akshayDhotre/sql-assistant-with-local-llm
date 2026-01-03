"""
Evaluation Report Generator

This module generates comprehensive evaluation reports with visualizations and analysis.
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class EvaluationReportGenerator:
    """Generate evaluation reports in multiple formats."""
    
    def __init__(self, output_dir: str = "evaluation_reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_json_report(
        self,
        evaluation_data: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Generate JSON report.
        
        Args:
            evaluation_data: Complete evaluation data dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(evaluation_data, f, indent=2)
        
        return str(filepath)
    
    def generate_markdown_report(
        self,
        evaluation_data: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Generate markdown report.
        
        Args:
            evaluation_data: Complete evaluation data dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_report_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(self._build_markdown_content(evaluation_data))
        
        return str(filepath)
    
    def _build_markdown_content(self, evaluation_data: Dict[str, Any]) -> str:
        """Build markdown report content."""
        lines = []
        
        # Header
        lines.append("# SQL Generation Evaluation Report\n")
        
        timestamp = evaluation_data.get("evaluation_timestamp", "N/A")
        lines.append(f"**Generated:** {timestamp}\n")
        
        # Executive Summary
        lines.append("## Executive Summary\n")
        
        model_summaries = evaluation_data.get("model_summaries", {})
        lines.append(f"- **Number of Models Evaluated:** {len(model_summaries)}\n")
        lines.append(f"- **Models:** {', '.join(model_summaries.keys())}\n")
        
        all_results = evaluation_data.get("all_results", {})
        total_tests = sum(
            len(results) for results in all_results.values()
        ) // len(model_summaries) if model_summaries else 0
        lines.append(f"- **Test Cases:** {total_tests}\n")
        
        # Best Models Section
        comparison = evaluation_data.get("comparison", {})
        best_models = comparison.get("best_models", {})
        
        lines.append("\n## Best Performing Models\n")
        
        if best_models.get("composite_score"):
            best_composite = best_models["composite_score"]
            lines.append(f"- **Composite Score:** {best_composite['model']} ({best_composite['score']:.4f})\n")
        
        if best_models.get("execution_rate"):
            best_exec = best_models["execution_rate"]
            lines.append(f"- **Execution Rate:** {best_exec['model']} ({best_exec['score']:.1f}%)\n")
        
        if best_models.get("validity_rate"):
            best_valid = best_models["validity_rate"]
            lines.append(f"- **Query Validity:** {best_valid['model']} ({best_valid['score']:.1f}%)\n")
        
        # Model Details
        lines.append("\n## Detailed Model Analysis\n")
        
        for model_name, summary in model_summaries.items():
            if "error" in summary:
                lines.append(f"\n### {model_name}\n")
                lines.append(f"**Status:** ❌ Error\n")
                lines.append(f"```\n{summary['error']}\n```\n")
                continue
            
            lines.append(f"\n### {model_name}\n")
            
            total = summary.get("total_tests", 0)
            valid = summary.get("valid_queries", 0)
            executed = summary.get("executed", 0)
            errors = summary.get("errors", 0)
            
            lines.append(f"**Test Results:**\n")
            lines.append(f"- Total Tests: {total}\n")
            lines.append(f"- Valid Queries: {valid}/{total} ({summary.get('valid_queries_pct', 0):.1f}%)\n")
            lines.append(f"- Executed Successfully: {executed}/{total} ({summary.get('executed_pct', 0):.1f}%)\n")
            lines.append(f"- Errors: {errors} ({summary.get('error_pct', 0):.1f}%)\n")
            
            # Similarity Metrics
            sim_metrics = summary.get("similarity_metrics", {})
            if sim_metrics:
                lines.append(f"\n**Similarity Metrics:**\n")
                lines.append(f"| Metric | Score |\n")
                lines.append(f"|--------|-------|\n")
                
                for metric_name, score in sim_metrics.items():
                    lines.append(f"| {metric_name.replace('_', ' ').title()} | {score:.4f} |\n")
                
                lines.append(f"\n- **Composite Score:** {summary.get('composite_score', 0):.4f}\n")
            
            lines.append("\n")
        
        # Sample Test Cases
        lines.append("\n## Sample Evaluations\n")
        lines.append("*Showing first 3 test results per model*\n")
        
        for model_name, results in all_results.items():
            lines.append(f"\n### {model_name}\n")
            
            for i, result in enumerate(results[:3]):
                lines.append(f"\n#### Test Case {result.get('test_id', i+1)}\n")
                lines.append(f"**Question:** {result.get('question', 'N/A')}\n")
                lines.append(f"**Status:** {'✅ Success' if result.get('execution_success') else '❌ Failed'}\n")
                
                gen_query = result.get("generated_query", "")
                if gen_query:
                    lines.append(f"\n**Generated Query:**\n")
                    lines.append(f"```sql\n{gen_query}\n```\n")
                
                exp_query = result.get("expected_query", "")
                if exp_query:
                    lines.append(f"\n**Expected Query:**\n")
                    lines.append(f"```sql\n{exp_query}\n```\n")
                
                # Metrics
                sim = result.get("similarity_metrics", {})
                if sim:
                    lines.append(f"\n**Metrics:**\n")
                    lines.append(f"- Composite Score: {result.get('composite_score', 0):.4f}\n")
                    lines.append(f"- BLEU Score: {sim.get('bleu_score', 0):.4f}\n")
                    lines.append(f"- F1 Score: {sim.get('f1_score', 0):.4f}\n")
                
                # Performance
                lines.append(f"\n**Performance:**\n")
                lines.append(f"- Generation Time: {result.get('generation_time_sec', 0)}s\n")
                lines.append(f"- Execution Time: {result.get('execution_time_sec', 0)}s\n")
        
        # Recommendations
        lines.append("\n## Recommendations\n")
        lines.append(self._generate_recommendations(evaluation_data))
        
        return "".join(lines)
    
    def _generate_recommendations(self, evaluation_data: Dict[str, Any]) -> str:
        """Generate recommendations based on evaluation results."""
        recommendations = []
        
        model_summaries = evaluation_data.get("model_summaries", {})
        
        # Find best model
        best_model = max(
            ((name, summary) for name, summary in model_summaries.items() if "error" not in summary),
            key=lambda x: x[1].get("composite_score", 0),
            default=(None, {})
        )
        
        if best_model[0]:
            recommendations.append(f"- Use **{best_model[0]}** as the primary model based on composite score.\n")
        
        # Execution rate analysis
        exec_rates = {
            name: summary.get("executed_pct", 0)
            for name, summary in model_summaries.items()
            if "error" not in summary
        }
        
        if exec_rates:
            min_exec_rate = min(exec_rates.values())
            if min_exec_rate < 80:
                recommendations.append("- Query execution rate is below 80%. Consider improving prompt engineering or guardrails.\n")
        
        # Validity analysis
        validity_rates = {
            name: summary.get("valid_queries_pct", 0)
            for name, summary in model_summaries.items()
            if "error" not in summary
        }
        
        if validity_rates:
            min_validity = min(validity_rates.values())
            if min_validity < 70:
                recommendations.append("- Query validation rate is below 70%. Review SQL guardrails and constraints.\n")
        
        if not recommendations:
            recommendations.append("- All models are performing well. No critical issues detected.\n")
        
        return "".join(recommendations)
    
    def generate_csv_report(
        self,
        evaluation_data: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Generate CSV report with detailed results.
        
        Args:
            evaluation_data: Complete evaluation data dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_results_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # Collect all results
        rows = []
        all_results = evaluation_data.get("all_results", {})
        
        headers = [
            "Model", "Test ID", "Valid", "Executed", "Generation Time (s)",
            "Execution Time (s)", "Exact Match", "Token Match", "BLEU Score",
            "F1 Score", "Semantic Similarity", "Composite Score"
        ]
        
        for model_name, results in all_results.items():
            for result in results:
                sim = result.get("similarity_metrics", {})
                row = [
                    result.get("model", model_name),
                    result.get("test_id", ""),
                    result.get("is_valid", False),
                    result.get("execution_success", False),
                    result.get("generation_time_sec", 0),
                    result.get("execution_time_sec", 0),
                    sim.get("exact_match", ""),
                    sim.get("token_match", ""),
                    sim.get("bleu_score", ""),
                    sim.get("f1_score", ""),
                    sim.get("semantic_similarity", ""),
                    result.get("composite_score", ""),
                ]
                rows.append(row)
        
        # Write CSV
        with open(filepath, 'w') as f:
            # Header
            f.write(",".join(headers) + "\n")
            
            # Data rows
            for row in rows:
                row_str = ",".join(str(v) for v in row)
                f.write(row_str + "\n")
        
        return str(filepath)
    
    def generate_all_reports(
        self,
        evaluation_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate all available report formats.
        
        Args:
            evaluation_data: Complete evaluation data dictionary
            
        Returns:
            Dictionary mapping report types to file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        reports = {
            "json": self.generate_json_report(evaluation_data, f"report_{timestamp}.json"),
            "markdown": self.generate_markdown_report(evaluation_data, f"report_{timestamp}.md"),
            "csv": self.generate_csv_report(evaluation_data, f"results_{timestamp}.csv"),
        }
        
        return reports
