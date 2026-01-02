# Setup Guide

This guide covers setup using **Ollama** for model management. Ollama works on all platforms and is the recommended approach.

## ⚡ Quick Start (All Platforms)

**See [OLLAMA_QUICKSTART.md](OLLAMA_QUICKSTART.md) for fastest setup** (5 minutes)

---

## 📋 Full Setup Steps

### 1. Install Ollama

Download and install from [ollama.ai](https://ollama.ai):

- **macOS**: [ollama-darwin.zip](https://ollama.ai/download/ollama-darwin.zip)
- **Linux**: [ollama-linux-x86_64.tgz](https://ollama.ai/download/ollama-linux-x86_64.tgz)  
- **Windows**: [ollama-windows-amd64.exe](https://ollama.ai/download/ollama-windows-amd64.exe)

Or use your package manager:

```bash
# macOS with Homebrew
brew install ollama

# Linux (Ubuntu/Debian)
curl https://ollama.ai/install.sh | sh

# Windows with Chocolatey
choco install ollama
```

### 2. Start Ollama Service

```bash
ollama serve
```

This starts the Ollama API on `http://localhost:11434`

### 3. Pull a Model

In a new terminal:

```bash
# Recommended: phi (fast, 2.7B)
ollama pull phi

# Alternative options:
ollama pull mistral      # 7B, more capable
ollama pull neural-chat  # 13B, better reasoning
ollama pull llama2       # 7B/13B, high quality
```

### 4. Clone Repository

```bash
git clone <repo-url>
cd sql-assistant-with-local-llm
```

### 5. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 6. Install Dependencies

All platforms use the same requirements:

```bash
pip install -r requirements.txt
```

This is much simpler than before - no platform-specific packages needed!

### 7. Configure (Optional)

Edit `config.yaml` if you want to:
- Use a different model
- Connect to remote Ollama
- Adjust temperature

```yaml
llm:
  base_url: "http://localhost:11434"
  model_name: "phi"           # Change to your model
  temperature: 0.1
```

### 8. Run Application

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## 🖥️ Platform-Specific Notes

### 🍎 macOS

**Advantages**:
- Automatic Metal GPU acceleration (Apple Silicon)
- Easy installation via Homebrew
- Works on both Intel and Apple Silicon

**Setup**:
```bash
brew install ollama
ollama serve
# In new terminal:
ollama pull phi
```

**Performance**:
- Apple Silicon: ~1-3 sec/query
- Intel: ~2-5 sec/query

---

### 🐧 Linux

**Advantages**:
- Full NVIDIA CUDA support
- Fastest performance with GPU
- Best for production deployments

**NVIDIA GPU Setup**:
```bash
# Ensure NVIDIA drivers installed
nvidia-smi

# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start service
ollama serve
```

**CPU-Only Setup**:
```bash
# Same as above, Ollama handles CPU-only mode automatically
```

**Performance**:
- NVIDIA GPU: ~0.5-2 sec/query
- CPU: ~2-5 sec/query

---

### 🪟 Windows

**Advantages**:
- DirectML GPU support
- Easy installer
- Compatible with most hardware

**Setup**:
1. Download installer from [ollama.ai](https://ollama.ai)
2. Run installer
3. Open PowerShell:
```powershell
ollama serve
# In new PowerShell:
ollama pull phi
```

**Performance**:
- With GPU: ~1-3 sec/query
- CPU-only: ~2-5 sec/query

**Full guide**: [SETUP_LINUX.md](SETUP_LINUX.md)

**Estimated setup time**: 20-40 minutes (GPU setup adds time)

---

### 🪟 Windows

**When to use**: You're developing on Windows

**Installation file**: `requirements.txt`

**Key differences**:
- Standard requirements file
- DirectML GPU support available (optional)
- Similar to Linux but using Windows paths
- Good for development

**Quick start**:
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Setup guide**: Use Linux guide but with Windows paths

**Estimated setup time**: 15-30 minutes

---

## Feature Comparison

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| GPU Support | Metal (slower) | CUDA (fast) | DirectML |
| Python 3.10+ | ✅ | ✅ | ✅ |
| Streamlit | ✅ | ✅ | ✅ |
| Model Download | ✅ | ✅ | ✅ |
| Development | ✅ Recommended | ✅ | ✅ |
| Production | ❌ Limited | ✅ Best | ❌ Limited |
| Docker | ✅ | ✅ | ✅ |
| Cost | Free | Free | Free |

---

## Requirements File Comparison

### Size & Content

```
requirements-macos.txt    904 B  - No CUDA packages
requirements-linux.txt   1.3 KB - Full CUDA 12.0 support
requirements.txt        1.3 KB - Generic (Windows/CUDA)
```

### What's Different

**Removed in `requirements-macos.txt`**:
- nvidia-cublas-cu12
- nvidia-cuda-cupti-cu12
- nvidia-cuda-nvrtc-cu12
- nvidia-cuda-runtime-cu12
- nvidia-cudnn-cu12
- nvidia-cufft-cu12
- nvidia-curand-cu12
- nvidia-cusolver-cu12
- nvidia-cusparse-cu12
- nvidia-nccl-cu12
- nvidia-nvjitlink-cu12
- nvidia-nvtx-cu12
- triton

These CUDA packages don't work on macOS and are only needed on Linux/Windows with NVIDIA GPUs.

---

## Installation Decision Tree

```
Do you have an NVIDIA GPU?
│
├─ YES, and on Linux
│  └─ Use: requirements-linux.txt
│     Config: gpu_layers: 20-30
│     Speed: ⚡⚡⚡ Very Fast
│
├─ YES, but on Mac/Windows
│  └─ Use: requirements-macos.txt or requirements.txt
│     Config: gpu_layers: 0
│     Speed: ⚡ Slow (CPU fallback)
│
└─ NO GPU
   └─ Use: requirements-macos.txt
      Config: gpu_layers: 0
      Speed: ⚡ Slow (CPU only)
```

---

## Performance Expectations

### Inference Speed (SQL Generation)

| Setup | Time | Hardware |
|-------|------|----------|
| macOS M1/M2/M3 | 3-5 sec | CPU only |
| macOS Intel | 5-10 sec | CPU only |
| Linux CPU | 5-10 sec | CPU only |
| Linux GPU (4GB) | 1-2 sec | NVIDIA GTX 1050 |
| Linux GPU (6GB+) | 0.5-1 sec | NVIDIA RTX 3060 |
| Linux GPU (12GB+) | 0.2-0.5 sec | NVIDIA RTX 3090 |

---

## Installation Troubleshooting

### "No module named 'torch'"

**macOS/Linux**:
```bash
pip install --upgrade -r requirements-macos.txt
```

**Windows**:
```bash
pip install --upgrade -r requirements.txt
```

### "CUDA out of memory" (Linux only)

```yaml
# Reduce in config.yaml
llm:
  gpu_layers: 10  # Instead of 30
```

### "Port 8501 already in use"

```bash
# All platforms
streamlit run app.py --server.port 8502
```

### "Model file not found"

```bash
# Verify path
ls -lh models/phi-3-sql.Q4_K_M.gguf

# Re-download if needed
curl -L https://huggingface.co/omeryentur/phi-3-sql/resolve/main/phi-3-sql.Q4_K_M.gguf \
  -o models/phi-3-sql.Q4_K_M.gguf
```

---

## Recommended Setup by Use Case

### For Learning/Development
```
Platform: macOS or Linux
Requirements: requirements-macos.txt
GPU layers: 0
Time to setup: 15-20 minutes
Cost: Free
```

### For Production
```
Platform: Linux
Requirements: requirements-linux.txt
GPU: NVIDIA RTX 3060+ (6GB+)
GPU layers: 25-30
Time to setup: 30-40 minutes
Cost: GPU hardware required
```

### For Quick Testing
```
Platform: Any (prefer Linux)
Requirements: requirements-macos.txt
Using: Docker image
Time to setup: 5-10 minutes
Cost: Free
```

---

## Next Steps

1. **Choose your platform** above
2. **Follow the platform guide**:
   - macOS → [SETUP_MACOS.md](SETUP_MACOS.md)
   - Linux → [SETUP_LINUX.md](SETUP_LINUX.md)
   - Windows → Use Linux guide with Windows paths
3. **Test the installation**:
   ```bash
   streamlit run app.py
   ```
4. **Open browser**: `http://localhost:8501`

---

## FAQ

**Q: Can I use GPU on macOS?**
A: Not directly. macOS uses Metal for GPU. For CUDA, use Linux.

**Q: Should I use `uv` instead of `pip`?**
A: Yes! `uv` is faster. Install with `pip install uv`, then use `uv pip install -r requirements-macos.txt`

**Q: Can I run this in Docker?**
A: Yes! Use `docker-compose up --build` on any platform.

**Q: What if my OS isn't listed?**
A: Use `requirements-macos.txt` as a safe default (CPU-only).

**Q: How much disk space do I need?**
A: ~10GB total (models are 2-4GB, rest is packages and data)

---

## Version Information

- **Created**: January 2, 2026
- **Python versions**: 3.10, 3.11, 3.12 supported
- **Tested platforms**: macOS 12+, Ubuntu 20.04+, Debian 11+
- **Latest requirements**: Updated for latest stable packages
