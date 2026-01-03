# SQL Assistant with Ollama

A modern Streamlit-based SQL chatbot that converts natural language questions into SQL queries using Ollama LLM service. Platform-independent and easy to deploy!

## Features

- **🤖 Natural Language to SQL**: Convert plain English questions to SQL queries using LLM
- **🐳 Ollama Integration**: Uses Ollama service for model management - no manual model downloads needed
- **🔒 Security First**: Built-in SQL injection prevention and query validation
- **📊 Real-time Execution**: Execute generated queries and display results immediately
- **🏗️ Modular Architecture**: Clean, well-organized codebase with separation of concerns
- **🧪 Comprehensive Testing**: Unit tests for validation and SQL generation
- **📦 Docker Ready**: Containerized deployment with docker-compose
- **🌍 Platform Independent**: Works on macOS, Linux, and Windows with Ollama

## What is Ollama?

[Ollama](https://ollama.ai) is a powerful tool for running open-source LLMs locally. Instead of downloading large model files manually, Ollama:
- Manages models automatically
- Provides a simple API endpoint
- Works on any platform (macOS, Linux, Windows)
- Supports GPU acceleration where available
- Simplifies model switching and updates

## Project Structure

```
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

```bash
# Recommended models for SQL generation:
ollama pull phi          # 2.7B - Fast, good quality (default)
ollama pull mistral      # 7B - Balanced performance
ollama pull neural-chat  # 13B - More capable
ollama pull llama2       # 7B/13B - High quality
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

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
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
  path: "students_data_multi_table.db"
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

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
llm:
  base_url: "http://localhost:11434"
  model_name: "phi"
  temperature: 0.1
  max_retries: 3                    # Intelligent retry for invalid SQL
  enable_result_formatting: false   # AI-powered result insights
```

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

### Configuration Presets

**Fast & Simple** (quick queries):
```yaml
llm:
  max_retries: 1
  enable_result_formatting: false
  model_name: "phi"
```

**Balanced** (recommended):
```yaml
llm:
  max_retries: 3
  enable_result_formatting: false
  model_name: "mistral"
```

**Maximum Reliability** (critical queries):
```yaml
llm:
  max_retries: 5
  enable_result_formatting: true
  model_name: "llama2"
```

## Module Overview

### LLM Module (`llm/`)
- **loader.py**: Ollama HTTP client for LLM service connection
- **prompts.py**: Prompt templates for SQL generation and result analysis
- **inference.py**: Functions for LLM inference
  - `get_response_from_llm_model()`: Generate SQL from natural language
  - `get_result_summary()`: Analyze and summarize query results

### SQL Module (`sql/`)
- **executor.py**: Database connections and query execution
- **validator.py**: Query syntax and safety validation
- **generator.py**: SQL extraction and cleaning from LLM output
- **schema_introspector.py**: Introspects database schema

### Security Module (`security/`)
- **sql_guardrails.py**: SQL injection prevention and dangerous query detection
  - Pattern-based injection detection
  - Dangerous keyword filtering
  - Query sanitization

### Evaluation Module (`evaluation/`)
- **metrics.py**: 5 semantic evaluation metrics (exact match, token match, BLEU, F1, semantic similarity)
- **run_eval.py**: Multi-model evaluation engine with detailed tracking
- **evaluate_models.py**: CLI pipeline for evaluating multiple models
- **report_generator.py**: Report generation (JSON, Markdown, CSV)
- **dataset.json**: Sample test cases for evaluation

### Core Module (`core/`)
- **logging.py**: App-wide logging system (replaces evaluation/logger.py) for tracking all application operations
- Dual output: Console (INFO) + File (DEBUG level)
- Persistent timestamped log files in `app_logs/`
- Used by evaluation and extensible for other modules

## Logging & Monitoring

✅ **Application-Wide Logging System**
- Centralized logger in `core/logging.py`
- Dual output: Console (INFO) + File (DEBUG)
- Persistent log files with timestamps in `app_logs/`
- Function name and line number context in detailed logs
- All evaluation attempts tracked
- Success and failure details captured

📊 **Evaluation Reports**
- JSON format for machine readability
- Markdown format for human readability
- CSV format for data analysis
- Model comparison reports
- Detailed metrics per test case

📚 **Documentation**
- [LOGGING_GUIDE.md](LOGGING_GUIDE.md) - Complete logging reference
- [LOGGING_EXAMPLES.md](LOGGING_EXAMPLES.md) - Log patterns and examples
- [LOGGING_QUICKSTART.md](LOGGING_QUICKSTART.md) - Quick start guide
- [LOGGING_IMPLEMENTATION_SUMMARY.md](LOGGING_IMPLEMENTATION_SUMMARY.md) - Technical details

## Security Features

✅ **Query Validation**
- Syntax checking
- Bracket and quote matching
- Parameter validation

✅ **SQL Injection Prevention**
- Dangerous keyword detection
- Pattern-based injection detection
- Statement separation validation

✅ **Query Restrictions**
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

## Models Available via Ollama

For SQL generation tasks, these models work well:

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| phi | 2.7B | ⚡⚡⚡ | Fast queries (default) |
| mistral | 7B | ⚡⚡ | Balanced performance |
| neural-chat | 13B | ⚡⚡ | Complex queries |
| llama2 | 7B/13B | ⚡ | Maximum quality |

Install via: `ollama pull <model_name>`

Full model library: [ollama.ai/library](https://ollama.ai/library)


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