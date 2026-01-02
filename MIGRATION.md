# Migration Guide from Old to New Structure

## Overview

This document guides you through migrating from the flat codebase structure to the new modular structure.

## What Changed

### Old Structure
```
├── app.py
├── load_llm_model.py
├── load_sql_database.py
├── config.json
└── requirements.txt
```

### New Structure
```
├── app.py (updated)
├── config.yaml (replaces config.json)
├── config.py (new)
├── llm/
│   ├── loader.py (from load_llm_model.py)
│   ├── prompts.py (new)
│   └── inference.py (from load_llm_model.py)
├── sql/
│   ├── executor.py (from load_sql_database.py)
│   ├── generator.py (new)
│   ├── validator.py (new)
│   └── schema_introspector.py (new)
├── security/
│   └── sql_guardrails.py (new)
├── evaluation/
│   ├── dataset.json (new)
│   ├── metrics.py (new)
│   └── run_eval.py (new)
└── tests/
    └── test_sql_generation.py (new)
```

## Migration Steps

### 1. Backup Old Files
```bash
mkdir backup
cp app.py load_llm_model.py load_sql_database.py config.json backup/
```

### 2. Update Imports in Your Code

**Old imports:**
```python
import load_sql_database
import load_llm_model

db_connection, cursor = load_sql_database.get_database_connection(DB_PATH)
llm = load_llm_model.get_llm_model(model_path, model_type, gpu_layers)
```

**New imports:**
```python
from sql import get_database_connection, execute_query
from llm import get_llm_model, get_response_from_llm_model

db_connection, cursor = get_database_connection(DB_PATH)
llm = get_llm_model(model_path, model_type, gpu_layers)
```

### 3. Update Configuration

**Old `config.json`:**
```json
{
    "DB_PATH": "students_data_multi_table.db",
    "LLM_PATH": "models/phi-3-sql.Q4_K_M.gguf",
    "MODEL_TYPE": "mistral",
    "GPU_LAYERS": 30
}
```

**New `config.yaml`:**
```yaml
llm:
  model_path: "models/phi-3-sql.Q4_K_M.gguf"
  model_type: "mistral"
  gpu_layers: 30

database:
  path: "students_data_multi_table.db"
```

**Loading configuration:**
```python
# Old way
with open('config.json', 'r') as f:
    config = json.load(f)

# New way
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

### 4. Update Database Operations

**Old code:**
```python
db_connection, db_cursor = load_sql_database.get_database_connection(DB_PATH)
sql_response = load_sql_database.execute_query(db_cursor, llm_response)
```

**New code:**
```python
from sql import get_database_connection, execute_query
from sql.validator import validate_query
from security.sql_guardrails import SQLGuardrails

db_connection, db_cursor = get_database_connection(DB_PATH)

# Validate query before execution
is_valid, msg = validate_query(llm_response)
is_safe, msg = SQLGuardrails.check_query_safety(llm_response)

if is_valid and is_safe:
    sql_response = execute_query(db_cursor, llm_response)
```

### 5. Update LLM Operations

**Old code:**
```python
from load_llm_model import get_llm_model, get_response_from_llm_model

llm = get_llm_model(model_path, model_type, gpu_layers)
prompt, response = get_response_from_llm_model(llm, schema, question)
```

**New code:**
```python
from llm import get_llm_model, get_response_from_llm_model
from llm.prompts import get_sql_generation_prompt

llm = get_llm_model(model_path, model_type, gpu_layers)
prompt, response = get_response_from_llm_model(llm, schema, question)

# Optionally use custom prompts
custom_prompt = get_sql_generation_prompt(schema, question)
```

## Benefits of New Structure

1. **Modularity**: Clear separation of concerns
2. **Scalability**: Easier to add new features
3. **Testability**: Dedicated test module
4. **Security**: Centralized security checks
5. **Configuration**: YAML-based config is more flexible
6. **Documentation**: Each module has clear purpose
7. **Maintainability**: Better code organization

## File Mappings

| Old File | New Location | Notes |
|----------|-------------|-------|
| `load_llm_model.py` | `llm/loader.py`, `llm/inference.py` | Split by responsibility |
| `load_sql_database.py` | `sql/executor.py` | Core database operations |
| `config.json` | `config.yaml` | YAML format, cleaner syntax |
| (new) | `sql/validator.py` | Query validation |
| (new) | `sql/generator.py` | SQL extraction from LLM |
| (new) | `sql/schema_introspector.py` | Schema inspection |
| (new) | `security/sql_guardrails.py` | Security checks |
| (new) | `llm/prompts.py` | Prompt templates |
| (new) | `evaluation/` | Testing and evaluation |

## Updating Custom Scripts

If you have custom scripts using the old modules:

```python
# Old way to load database
import load_sql_database

connection, cursor = load_sql_database.get_database_connection('db.db')
load_sql_database.execute_queries(cursor, queries_list)
load_sql_database.commit_db_changes(connection)
```

```python
# New way
from sql import get_database_connection, execute_queries, commit_db_changes

connection, cursor = get_database_connection('db.db')
execute_queries(cursor, queries_list)
commit_db_changes(connection)
```

## Running Tests

New test suite is available:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_sql_generation.py::TestSQLValidator::test_valid_select_query -v
```

## Docker Deployment

New Dockerfile and docker-compose.yml simplify deployment:

```bash
# Build and run
docker-compose up --build

# Run single container
docker build -t sql-assistant .
docker run -p 8501:8501 sql-assistant
```

## Questions?

Refer to the main [README.md](README.md) for more details on the new architecture.
