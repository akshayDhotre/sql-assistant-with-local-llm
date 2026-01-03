# SQL Assistant with Local LLM

**Natural Language → SQL System**

A **secure, modular, and evaluation-driven Text-to-SQL assistant** that converts natural language questions into **validated SQL queries** using a **local LLM (Ollama)**, executes them safely on a database, and returns structured results with explanations.

This project goes beyond a demo chatbot and focuses on **real-world concerns** like SQL safety, schema awareness, observability, evaluation, and reproducibility.

## Key Features

### SQL Safety & Guardrails

- SELECT-only enforcement  
- SQL injection prevention  
- Blocking of destructive keywords (`DROP`, `DELETE`, `UPDATE`, etc.)  
- Query sanitization and row-limit enforcement  

### Schema-Aware SQL Generation

- Database schema introspection  
- Context-aware prompt construction  
- Restricts LLM to **only valid tables and columns**

### Evaluation-Driven Design

- Offline evaluation harness for NL → SQL
- Metrics:
  - Exact match
  - Semantic similarity
  - Execution success rate
  - Latency
- Supports **multi-model benchmarking**

### Interactive Streamlit UI

- Natural language input
- Generated SQL visibility toggle
- Query execution results
- Error explanations in plain English

### Observability & Logging

- Query lifecycle logging
- Latency tracking
- Error diagnostics
- Configurable log levels

### Testing & Reliability

- Unit tests for SQL validation, guardrails, and generation
- Structured project layout for maintainability

### Dockerized Deployment

- One-command setup using Docker Compose
- Environment-agnostic execution

## What is Ollama?

[Ollama](https://ollama.ai) is a powerful tool for running open-source LLMs locally.
Instead of downloading large model files manually, Ollama:

- Manages models automatically
- Provides a simple API endpoint
- Works on any platform (macOS, Linux, Windows)
- Supports GPU acceleration where available
- Simplifies model switching and updates

## Architecture Overview

```bash
User
 ↓
Streamlit UI
 ↓
Query Understanding
 ↓
Schema-Aware Prompt Builder
 ↓
Local LLM (Ollama)
 ↓
SQL Validator & Guardrails
 ↓
Database Executor (Read-Only)
 ↓
Result Formatter & Explanation
 ↓
User
```

## Design Decisions & Tradeoffs

This project was **intentionally designed as a production-oriented LLM system**, not just a proof-of-concept chatbot. Below are some key architectural decisions and the tradeoffs involved.

### Local LLM vs Cloud API

**Decision**: Use a local LLM (via Ollama) instead of a hosted API.

- **Why**: Ensures data privacy for database queries, enables cost-efficient experimentation, and provides full control over inference and latency.
- **Tradeoff**: Local models may be less capable than large hosted models, requiring stronger prompting, validation, and retries — which this system explicitly implements.

### Explicit SQL Guardrails

**Decision**: Enforce SQL safety using deterministic validation and guardrails, not just prompt instructions.

- **Why**: LLMs are probabilistic and cannot be fully trusted for safety. Explicit checks prevent destructive queries regardless of model behavior and align with enterprise security expectations.
- **Tradeoff**: Adds extra validation logic and complexity, but significantly improves reliability and trust.

### Schema-Aware Prompting

**Decision**: Dynamically extract and inject only relevant schema context into prompts.

- **Why**: Reduces prompt noise and token usage, improves SQL accuracy, and limits the LLM to valid tables and columns.
- **Tradeoff**: Requires additional schema introspection logic, but results in more predictable outputs.

### Evaluation as a First-Class Component

**Decision**: Build an offline evaluation harness separate from the UI.

- **Why**: Enables reproducible benchmarking, allows comparison across models, and treats LLM behavior as something to be measured, not assumed.
- **Tradeoff**: Slower initial development, but critical for long-term maintainability and improvement.

### Modular Architecture

**Decision**: Separate concerns into clear modules (LLM, SQL generation, validation, execution, evaluation).

- **Why**: Improves testability and maintainability, enables future extensions (multi-DB support, API layer), and reflects real production system boundaries.
- **Tradeoff**: More files and upfront structure, but far easier to evolve and reason about.

### Streamlit UI with Decoupled Logic

**Decision**: Use Streamlit for rapid interaction while keeping core logic UI-agnostic.

- **Why**: Allows quick experimentation and demos while ensuring core logic can be reused in APIs or services.
- **Tradeoff**: Streamlit is not a full frontend framework, but sufficient for exploration and validation.

### AI-Assisted Coding

**Decision**: Use AI coding assistants for boilerplate and refactoring, while retaining full control over architecture.

- **Why**: Speeds up development and allows focus on higher-level system design and decision-making.
- **Tradeoff**: Requires careful review and ownership of all generated code, which this project maintains.

### Overall Philosophy

The core philosophy of this project is to treat LLMs as **unreliable but powerful components** within a larger system — not as autonomous decision-makers.

The design emphasizes:

- **Safety** over blind capability
- **Evaluation** over assumptions
- **Deterministic controls** around probabilistic models

This mirrors how LLM systems are increasingly built in real-world production environments.

## Project Structure

```bash
sql_assistant/
├── app.py                    # Streamlit entry point
├── config.yaml               # Configuration (Ollama endpoint, model, DB, security)
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose orchestration
│
├── llm/                      # LLM module
│   ├── __init__.py
│   ├── loader.py             # Ollama client
│   ├── prompts.py            # Prompt templates (SQL generation & result analysis)
│   └── inference.py          # Query generation & result summary inference
│
├── sql/                      # SQL handling module
│   ├── __init__.py
│   ├── schema_introspector.py # Database schema inspection
│   ├── generator.py          # SQL query generation utilities
│   ├── validator.py          # Query validation & syntax checking
│   └── executor.py           # Database operations
│
├── security/                 # Security module
│   └── sql_guardrails.py    # SQL injection prevention
│
├── evaluation/               # Evaluation module
│   ├── dataset.json          # Test dataset
│   ├── metrics.py            # Evaluation metrics
│   └── run_eval.py           # Evaluation runner
│
├── tests/                    # Unit tests
│   └── test_sql_generation.py
│
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore
```

## Installation

### Prerequisites

- Python 3.10+
- Pip package manager
- [Ollama](https://ollama.ai) installed and running
- 4GB+ RAM (for LLM inference)
- NVIDIA GPU (optional, for faster inference)

### Step 1: Install Ollama

Visit [ollama.ai](https://ollama.ai) and download the installer for your platform:

- **macOS**: Metal GPU support (works on Intel and Apple Silicon)
- **Linux**: NVIDIA CUDA support (with proper drivers)
- **Windows**: GPU support (with NVIDIA drivers)

### Step 2: Pull a Model

Once Ollama is installed and running, pull a model:

Full model library: [ollama.ai/library](https://ollama.ai/library)

```bash
# Recommended models for SQL generation:
ollama pull llama3       # 7B/13B - High quality
```

You can list installed models with:

```bash
ollama list
```

### Step 3: Clone and Setup Repository

1. **Clone the repository**:

   ```bash
   git clone <repo-url>
   cd sql-assistant-with-local-llm
   ```

2. **Using uv for python project manager**

   ```bash
   uv sync
   
   # UV commands
   uv run python -m your_module
   # or
   uv run pytest
   ```

3. **Create virtual environment** (non uv based setup):

   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   
   # Install dependencies**:
   pip install -r requirements.txt
   ```

### Step 4: Configure Application

Edit `config.yaml`:

```yaml
llm:
  base_url: "http://localhost:11434"      # Ollama service endpoint
  model_name: "llama3:latest"                        # Model name (must be pulled via: ollama pull)
  temperature: 0.1                         # Lower = more deterministic, better for SQL
  max_retries: 3                           # Retry invalid SQL generation (1-5)
  enable_result_formatting: false          # AI-powered result insights (slower)

database:
  path: "students_data_multi_table.db"    # SQLite database file path
  type: "sqlite"

security:
  max_queries_per_minute: 100
  max_result_rows: 10000
  enable_guardrails: true
```

### Step 5: Setup Database (optional)

```bash
python load_sql_database.py
```

## Usage

### Ensure Ollama is Running

```bash
# Ollama typically starts automatically on system launch
# If not running, start it manually:
ollama serve
```

You should see the server running on `http://localhost:11434`

### Running the Application Locally

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Using Docker

```bash
# Build and run with docker-compose (includes Ollama service)
docker-compose up --build

# Or run the container directly
docker build -t sql-assistant .
docker run -p 8501:8501 sql-assistant
```

**Note**: If using Docker, ensure Ollama is running on the host or modify the connection URL.

### Retry Logic

When the LLM generates invalid SQL, the system automatically retries up to `max_retries` times:

- **Automatic**: No user action needed
- **Validates**: Both syntax and security checked on each attempt
- **Transparent**: User sees attempt progress

### Result Formatting

When enabled (`enable_result_formatting: true`), generates natural language insights:

- Smart analysis of patterns in results
- Contextual summary based on original question
- Optional expandable section in UI

## Logging & Monitoring

### Application-Wide Logging System

- Centralized logger in `core/logging.py`
- Dual output: Console (INFO) + File (DEBUG)
- Persistent log files with timestamps in `app_logs/`
- Function name and line number context in detailed logs
- All evaluation attempts tracked
- Success and failure details captured

### Evaluation Reports

- JSON format for machine readability
- Markdown format for human readability
- CSV format for data analysis
- Model comparison reports
- Detailed metrics per test case

## Security Features

### Query Validation

- Syntax checking
- Bracket and quote matching
- Parameter validation

### SQL Injection Prevention

- Dangerous keyword detection
- Pattern-based injection detection
- Statement separation validation

### Query Restrictions

- SELECT-only enforcement (read-only)
- Comment removal
- Rate limiting support

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Or run specific tests:

```bash
python -m pytest tests/test_sql_generation.py::TestSQLValidator -v
```

## Troubleshooting

### Ollama Service Not Available

- Ensure Ollama is installed from [ollama.ai](https://ollama.ai)
- Start Ollama service: `ollama serve`
- Check connectivity: `curl http://localhost:11434/api/tags`
- For remote Ollama, update `base_url` in config.yaml

### Model Not Found

- List available models: `ollama list`
- Pull model: `ollama pull phi`
- Verify model name matches `model_name` in config.yaml

### Slow Query Generation

- Try smaller model: `phi` (2.7B) instead of larger ones
- Check Ollama memory usage
- Enable GPU acceleration (if available)
- Increase timeout in connection settings

### Database Connection Issues

- Verify database file exists and is readable
- Check `database.path` in config.yaml
- Ensure SQLite is installed

## Performance

- **CPU (phi model)**: ~2-5 sec per query
- **GPU (NVIDIA)**: ~0.5-2 sec per query
- **macOS (Metal)**: ~1-3 sec per query

**Tips for faster performance:**

- Use smaller models (phi is recommended)
- Ensure GPU drivers are up-to-date
- Close unnecessary applications
- Adjust temperature (lower = faster, less creative)

## Future Enhancements

- [ ] Multi-turn conversation support
- [ ] Query optimization suggestions
- [ ] Schema update detection
- [ ] Advanced caching
- [ ] PostgreSQL/MySQL support
- [ ] Batch query execution
- [ ] Query result visualization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Authors

- **Akshay Dhotre** - Initial development (July 2024)

## Acknowledgments

- [Ollama](https://ollama.ai) for the excellent local LLM service
- [Streamlit](https://streamlit.io/) for the web framework
- Open-source LLM community for providing accessible models
- [TheBloke](https://huggingface.co/TheBloke) for model quantization efforts

## Support

For issues and questions:

- Open an issue on GitHub
- Check existing documentation
- Review test cases for usage examples
