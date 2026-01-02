# macOS Setup Guide

Complete guide to setting up SQL Assistant on macOS.

## System Requirements

- **macOS**: 10.14 (Mojave) or higher
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB+ recommended for LLM)
- **Disk Space**: 10GB+ (for models)

## Installation Steps

### 1. Check Python Version

```bash
python3 --version
# Should be 3.10 or higher
```

If you need Python 3.10+, install via:

**Using Homebrew (Recommended)**:
```bash
brew install python@3.11
```

**Using MacPorts**:
```bash
sudo port install python311
```

**Using Conda**:
```bash
conda create -n sql-assistant python=3.11
conda activate sql-assistant
```

### 2. Clone Repository

```bash
git clone <repo-url>
cd sql-assistant-with-local-llm
```

### 3. Create Virtual Environment

```bash
# Using venv (built-in)
python3 -m venv venv
source venv/bin/activate

# Or using Conda
conda create -n sql-assistant python=3.11
conda activate sql-assistant
```

### 4. Install Dependencies

**For macOS (Apple Silicon - M1/M2/M3):**
```bash
pip install -r requirements-macos.txt
```

**For macOS (Intel):**
```bash
pip install -r requirements-macos.txt
```

**Alternative with uv (faster):**
```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv pip install -r requirements-macos.txt
```

### 5. Download LLM Model

Create models directory and download a GGUF format model:

```bash
mkdir -p models

# Option 1: phi-3-sql (Recommended - smaller, faster)
curl -L https://huggingface.co/omeryentur/phi-3-sql/resolve/main/phi-3-sql.Q4_K_M.gguf \
  -o models/phi-3-sql.Q4_K_M.gguf

# Option 2: nsql-llama-2
# curl -L https://huggingface.co/TheBloke/nsql-llama-2-7B-GGUF/resolve/main/nsql-llama-2-7b.Q5_K_M.gguf \
#   -o models/nsql-llama-2-7b.Q5_K_M.gguf
```

Alternatively, use [HuggingFace CLI](https://huggingface.co/docs/hub/security-tokens):

```bash
huggingface-cli download omeryentur/phi-3-sql phi-3-sql.Q4_K_M.gguf --local-dir ./models
```

### 6. Configure Application

Edit `config.yaml`:

```yaml
llm:
  model_path: "models/phi-3-sql.Q4_K_M.gguf"  # Update path if different
  model_type: "mistral"
  gpu_layers: 0  # macOS uses Metal, not CUDA layers (set to 0 or low value)
  temperature: 0.1

database:
  path: "students_data_multi_table.db"
  type: "sqlite"

security:
  max_queries_per_minute: 100
  max_result_rows: 10000
  enable_guardrails: true
```

### 7. (Optional) Create Sample Database

```bash
python load_sql_database.py
```

### 8. Run the Application

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

---

## Troubleshooting

### Issue: "No module named 'ctransformers'"

**Solution:**
```bash
pip install --upgrade ctransformers
```

### Issue: "Failed to load LLM model"

**Check**:
1. Model file path in `config.yaml` is correct
2. Model file exists: `ls -lh models/`
3. Sufficient disk space: `df -h`

**Solution**:
```bash
# Re-download the model
curl -L https://huggingface.co/omeryentur/phi-3-sql/resolve/main/phi-3-sql.Q4_K_M.gguf \
  -o models/phi-3-sql.Q4_K_M.gguf
```

### Issue: "Port 8501 already in use"

**Solution**:
```bash
# Run on different port
streamlit run app.py --server.port 8502

# Or kill existing process
lsof -i :8501
kill -9 <PID>
```

### Issue: "SQLite database connection error"

**Solution**:
```bash
# Check if database file exists
ls -lh *.db

# Recreate database
python load_sql_database.py
```

### Issue: "Slow inference on Mac"

This is normal for CPU-only inference. Try:
1. Use smaller quantized model (Q4 instead of Q5)
2. Increase timeout in Streamlit: `streamlit run app.py --client.toolbarMode=minimal`
3. Use Docker with GPU if available

### Issue: M1/M2 Compatibility

For Apple Silicon (M1/M2/M3), you may need:

```bash
# Use native Python for ARM
arch -arm64 python3 -m pip install -r requirements-macos.txt

# Or ensure Homebrew Python is ARM native
brew install python@3.11  # Installs native ARM version
```

---

## Performance Tips

### CPU Optimization
```bash
# Use smaller model quantization
# Q4 is faster than Q5 or Q6
# Download Q4_K_M or Q4_K_S variant
```

### Memory Optimization
```yaml
# In config.yaml, reduce batch size if memory issues
llm:
  max_tokens: 256  # Reduce if needed
```

### Model Selection

| Model | Size | Speed | Quality | Recommended |
|-------|------|-------|---------|-------------|
| phi-3-sql Q4_K_M | 2.3 GB | ⚡⚡⚡ Fast | Good | ✅ Yes |
| phi-3-sql Q5_K_M | 2.8 GB | ⚡⚡ Medium | Better | If you have RAM |
| nsql-llama-2 Q5_K_M | 4.1 GB | ⚡ Slow | Best | High-end Macs only |

---

## Development Setup

For development, install additional tools:

```bash
# Testing
pip install pytest pytest-cov

# Linting
pip install black flake8 pylint

# Type checking
pip install mypy

# All dev tools
pip install -r requirements-macos.txt pytest black flake8 mypy
```

Run tests:
```bash
pytest tests/ -v
```

---

## Using with Docker (Optional)

For consistency across machines:

```bash
# Build Docker image
docker build -t sql-assistant .

# Run container
docker run -p 8501:8501 -v $(pwd)/models:/app/models sql-assistant
```

Or with docker-compose:

```bash
docker-compose up --build
```

---

## Updating Dependencies

To update packages safely:

```bash
# Update single package
pip install --upgrade ctransformers

# Update all packages
pip install --upgrade -r requirements-macos.txt

# Check for security vulnerabilities
pip install safety
safety check
```

---

## Uninstalling

To remove the installation:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Or if using conda
conda deactivate
conda env remove -n sql-assistant
```

---

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [ctransformers on GitHub](https://github.com/marella/ctransformers)
- [GGUF Model Format](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [HuggingFace Models](https://huggingface.co/models)

---

## Getting Help

If you encounter issues:

1. **Check logs**: Scroll up in terminal for error messages
2. **Review config**: Ensure `config.yaml` is correct
3. **Test components**: Try importing modules directly
4. **Check disk space**: `df -h`
5. **Check RAM**: `top` or Activity Monitor
6. **Update packages**: `pip install --upgrade -r requirements-macos.txt`

---

**Last Updated**: January 2, 2026
