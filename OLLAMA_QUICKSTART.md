# Quick Start with Ollama

Get the SQL Assistant running with Ollama in 5 minutes.

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installed

## 1️⃣ Install & Start Ollama

```bash
# Download from https://ollama.ai
# Or use homebrew on macOS:
brew install ollama

# Start Ollama service
ollama serve
```

## 2️⃣ Pull a Model

In another terminal:

```bash
# Recommended for SQL (fast & good quality)
ollama pull phi

# Or try alternatives:
ollama pull mistral      # More capable
ollama pull neural-chat  # Better reasoning
```

## 3️⃣ Setup Python Environment

```bash
# Clone and navigate
git clone <repo-url>
cd sql-assistant-with-local-llm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 4️⃣ Configure (Optional)

Edit `config.yaml`:

```yaml
llm:
  base_url: "http://localhost:11434"
  model_name: "phi"  # Change to your model
  temperature: 0.1
```

## 5️⃣ Run!

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## Model Cheat Sheet

| Use Case | Model | Command |
|----------|-------|---------|
| Fast & Good | phi | `ollama pull phi` |
| Best Quality | llama2:13b | `ollama pull llama2:13b` |
| Balanced | mistral | `ollama pull mistral` |
| Lightweight | tinyllama | `ollama pull tinyllama` |

## Useful Commands

```bash
# List all models
ollama list

# Pull a new model
ollama pull neural-chat

# Remove a model
ollama rm phi

# Get API info
curl http://localhost:11434/api/tags
```

## Verify Setup

```bash
# Test Ollama is running
curl http://localhost:11434/api/tags

# Should return JSON with model info
```

## Common Issues

### ❌ "Connection refused"
```bash
# Start Ollama
ollama serve
```

### ❌ "Model not found"
```bash
# Pull the model
ollama pull phi
```

### ❌ "Slow responses"
- Use smaller model: `ollama pull phi`
- Check Ollama is using GPU: `ollama list`
- Restart Ollama service

## Done! 🎉

Your SQL Assistant is ready. Start asking questions in natural language!

---

For more details, see [README.md](README.md) or [OLLAMA_MIGRATION.md](OLLAMA_MIGRATION.md)
