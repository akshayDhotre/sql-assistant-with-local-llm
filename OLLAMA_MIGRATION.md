# Ollama Migration Guide

This document summarizes the migration from local GGUF model loading to Ollama-based LLM serving.

## What Changed

### ✅ Benefits of Ollama

1. **Platform Independent** - Works on macOS, Linux, and Windows without OS-specific setup
2. **No Model Downloads** - Ollama manages models automatically
3. **Easy Model Switching** - Change models with a simple CLI command
4. **GPU Support** - Automatic GPU acceleration when available
5. **Lightweight** - No need for heavy ML libraries per platform
6. **Community Models** - Access to 100+ models via Ollama library

## Files Modified

### 1. **llm/loader.py** - Complete Rewrite
**Old**: Used `ctransformers.AutoModelForCausalLM` to load GGUF files from disk
**New**: Uses `requests` library to communicate with Ollama API

```python
# Old way
from ctransformers import AutoModelForCausalLM
llm = AutoModelForCausalLM.from_pretrained("models/model.gguf", ...)

# New way
from llm import get_llm_model
llm = get_llm_model(ollama_base_url="http://localhost:11434", model_name="phi")
```

**Key improvements:**
- `OllamaClient` class wraps HTTP API calls
- `is_available()` checks if Ollama service is running
- Error handling for connection failures
- Compatible with same inference interface

### 2. **llm/inference.py** - Minor Update
Changed documentation from "loaded LLM model" to "Ollama LLM"
Functional interface remains the same

### 3. **config.yaml** - Configuration Changes
**Old**:
```yaml
llm:
  model_path: "models/phi-3-sql.Q4_K_M.gguf"
  model_type: "mistral"
  gpu_layers: 30
```

**New**:
```yaml
llm:
  base_url: "http://localhost:11434"
  model_name: "phi"
  temperature: 0.1
```

### 4. **app.py** - Updated Initialization
Changed `initialize_llm()` to use new Ollama parameters:
```python
# Old
get_llm_model(
    model_path=config["llm"]["model_path"],
    model_type=config["llm"]["model_type"],
    gpu_layers=config["llm"]["gpu_layers"]
)

# New
get_llm_model(
    ollama_base_url=config["llm"]["base_url"],
    model_name=config["llm"]["model_name"]
)
```

### 5. **requirements.txt** - Dependency Changes
**Removed**: `ctransformers==0.2.27`
- No more heavy ML framework dependencies
- Reduced file size and installation time

**Retained**: `requests==2.32.3` (already present)
- Used for HTTP communication with Ollama

### 6. **README.md** - Complete Documentation Update
- Removed GGUF model download instructions
- Added Ollama installation and setup guide
- Updated API usage examples
- Added model selection table
- Improved troubleshooting section
- Updated performance expectations

## Migration Steps for Users

### Step 1: Install Ollama
Visit [ollama.ai](https://ollama.ai) and download installer

### Step 2: Pull Models
```bash
# Run Ollama
ollama serve

# In another terminal, pull your model
ollama pull phi
ollama pull mistral
ollama pull neural-chat
```

### Step 3: Update Python Environment
```bash
# Remove old dependencies
pip uninstall ctransformers

# Install new dependencies (already in requirements.txt)
pip install -r requirements.txt
```

### Step 4: Update Configuration
Edit `config.yaml`:
```yaml
llm:
  base_url: "http://localhost:11434"
  model_name: "phi"
  temperature: 0.1
```

### Step 5: Run Application
```bash
# Start Ollama (if not already running)
ollama serve

# In another terminal
streamlit run app.py
```

## API Changes

### Model Initialization
```python
# Old
from llm.loader import get_llm_model
llm = get_llm_model(
    model_path="models/model.gguf",
    model_type="mistral",
    gpu_layers=30
)

# New
from llm.loader import get_llm_model
llm = get_llm_model(
    ollama_base_url="http://localhost:11434",
    model_name="phi"
)
```

### Model Inference
The inference interface remains **identical**:
```python
from llm import get_response_from_llm_model

prompt, response = get_response_from_llm_model(
    llm_model=llm,
    table_schema=schema,
    question="Your question"
)
```

## Performance Notes

### CPU Performance
- **phi (2.7B)**: 2-5 sec per query ✅ Recommended
- **neural-chat (13B)**: 5-10 sec per query
- **mistral (7B)**: 4-8 sec per query

### GPU Performance
- **NVIDIA GPU**: 0.5-2 sec per query (requires NVIDIA drivers)
- **macOS Metal**: 1-3 sec per query (automatic on Apple Silicon)

### Memory Requirements
- **phi**: ~3-4 GB RAM
- **neural-chat**: ~8-10 GB RAM
- **mistral**: ~5-6 GB RAM

## Troubleshooting

### Ollama Not Running
```bash
# Start Ollama service
ollama serve

# Test connectivity
curl http://localhost:11434/api/tags
```

### Model Not Found
```bash
# List available models
ollama list

# Pull needed model
ollama pull phi
```

### Connection Refused
1. Ensure Ollama is running: `ollama serve`
2. Check URL in config.yaml (default: http://localhost:11434)
3. For remote Ollama, update `base_url` accordingly

## Uninstalling Old Components

Old model files can be safely deleted:
```bash
# Safe to delete (Ollama manages models now)
rm -rf models/

# Keep everything else
```

## Benefits Summary

| Feature | Old (GGUF) | New (Ollama) |
|---------|-----------|-------------|
| Setup Complexity | High | Low ✅ |
| Platform Support | Windows-centric | Cross-platform ✅ |
| Model Management | Manual | Automatic ✅ |
| Model Switching | File replacement | Single command ✅ |
| GPU Support | Complex | Automatic ✅ |
| Dependencies | Heavy (ctransformers) | Light (requests) ✅ |
| Community Models | Limited | 100+ models ✅ |

## Questions?

For more information about Ollama:
- Visit [ollama.ai](https://ollama.ai)
- Check [Ollama GitHub](https://github.com/ollama/ollama)
- Browse [Model Library](https://ollama.ai/library)
