# Quick Reference Guide

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure the App
Edit `config.yaml`:
```yaml
llm:
  model_path: "models/your-model.gguf"
  model_type: "mistral"
  gpu_layers: 30

database:
  path: "your_database.db"
```

### 3. Run the App
```bash
streamlit run app.py
```

### 4. Open Browser
Navigate to `http://localhost:8501`

---

## 📚 Module Reference

### Import LLM Functions
```python
from llm import get_llm_model, get_response_from_llm_model
from llm.prompts import get_sql_generation_prompt
```

### Import SQL Functions
```python
from sql import (
    get_database_connection,
    execute_query,
    execute_queries,
    commit_db_changes,
    close_db_connection
)
from sql.validator import validate_query
from sql.schema_introspector import get_database_schema
from sql.generator import clean_sql_response, parse_sql_query
```

### Import Security Functions
```python
from security.sql_guardrails import SQLGuardrails
```

---

## 🔧 Common Tasks

### Load LLM Model
```python
from llm import get_llm_model

llm = get_llm_model(
    model_path="models/phi-3-sql.Q4_K_M.gguf",
    model_type="mistral",
    gpu_layers=30
)
```

### Connect to Database
```python
from sql import get_database_connection

connection, cursor = get_database_connection("database.db")
```

### Generate SQL from Question
```python
from llm import get_response_from_llm_model

prompt, sql_response = get_response_from_llm_model(
    llm_model=llm,
    table_schema="CREATE TABLE...",
    question="What is the average age?"
)
```

### Validate Query
```python
from sql.validator import validate_query
from security.sql_guardrails import SQLGuardrails

is_valid, msg = validate_query(sql_query)
is_safe, msg = SQLGuardrails.check_query_safety(sql_query)
```

### Execute Query
```python
from sql import execute_query

results = execute_query(cursor, "SELECT * FROM users")
for row in results.fetchall():
    print(row)
```

### Get Database Schema
```python
from sql.schema_introspector import get_database_schema

schema = get_database_schema(cursor)
print(schema)
```

---

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_sql_generation.py::TestSQLValidator -v
```

### Run Specific Test
```bash
python -m pytest tests/test_sql_generation.py::TestSQLValidator::test_valid_select_query -v
```

---

## 🐳 Docker

### Build Image
```bash
docker build -t sql-assistant .
```

### Run Container
```bash
docker run -p 8501:8501 sql-assistant
```

### Use Docker Compose
```bash
docker-compose up --build
```

---

## 📁 Directory Structure

```
llm/               - LLM model loading and inference
sql/               - SQL database operations
security/          - Security and validation
evaluation/        - Testing and metrics
tests/             - Unit tests

app.py             - Streamlit web interface
config.py          - Configuration loader
config.yaml        - Application settings
```

---

## 🔐 Security Best Practices

✅ Always validate queries before execution:
```python
is_valid, msg = validate_query(query)
if not is_valid:
    raise ValueError(msg)
```

✅ Always check security guardrails:
```python
is_safe, msg = SQLGuardrails.check_query_safety(query)
if not is_safe:
    raise ValueError(msg)
```

✅ Use parameterized queries when possible

✅ Never trust user input directly

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Full documentation |
| [MIGRATION.md](MIGRATION.md) | Migration from old structure |
| [STATUS.md](STATUS.md) | Restructuring status |
| [RESTRUCTURING_SUMMARY.md](RESTRUCTURING_SUMMARY.md) | What was changed |

---

## ⚡ Performance Tips

1. **Cache LLM model**:
   ```python
   @st.cache_resource
   def load_model():
       return get_llm_model(...)
   ```

2. **Use GPU acceleration**:
   Set `gpu_layers: 30` in config.yaml

3. **Optimize database queries**:
   Use indexes on frequently queried columns

4. **Limit result sets**:
   Set `max_result_rows: 10000` in config

---

## 🆘 Troubleshooting

### Model not loading?
- Check file path in config.yaml
- Verify GGUF format
- Ensure sufficient disk space

### Database connection failed?
- Verify database file exists
- Check database path in config.yaml
- Ensure file permissions

### Slow performance?
- Enable GPU layers if available
- Use smaller model
- Check system resources

---

## 💡 Examples

### Example 1: Simple Query
```python
from llm import get_llm_model, get_response_from_llm_model
from sql import get_database_connection, execute_query

# Setup
llm = get_llm_model("models/model.gguf", "mistral", 30)
conn, cursor = get_database_connection("db.sqlite")

# Generate SQL
_, sql = get_response_from_llm_model(
    llm, 
    "CREATE TABLE users (id INT, name TEXT)",
    "Get all users"
)

# Execute
results = execute_query(cursor, sql)
```

### Example 2: With Validation
```python
from sql.validator import validate_query
from security.sql_guardrails import SQLGuardrails

query = "SELECT * FROM users"

# Validate
is_valid, msg = validate_query(query)
assert is_valid, msg

# Security check
is_safe, msg = SQLGuardrails.check_query_safety(query)
assert is_safe, msg

# Execute
results = execute_query(cursor, query)
```

---

## 📞 Need Help?

1. **Check README.md** for full documentation
2. **Review MIGRATION.md** if moving from old code
3. **Look at tests/** for usage examples
4. **Check module docstrings** for API details

---

**Happy coding! 🎉**
