# Linux Setup Guide

Complete guide to setting up SQL Assistant on Linux (with optional GPU support).

## System Requirements

- **Linux**: Ubuntu 20.04+ / Debian 11+ / RHEL 8+
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB+ recommended for LLM)
- **Disk Space**: 10GB+ (for models)
- **GPU** (Optional): NVIDIA GPU with CUDA 12.0+

## Installation Steps

### 1. Update System

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get upgrade -y

# RHEL/CentOS/Fedora
sudo dnf update -y
```

### 2. Install Python

**Ubuntu/Debian:**
```bash
sudo apt-get install python3.11 python3.11-venv python3.11-dev -y
```

**RHEL/CentOS/Fedora:**
```bash
sudo dnf install python3.11 python3.11-devel -y
```

**Verify installation:**
```bash
python3.11 --version
```

### 3. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential curl wget git -y
```

**RHEL/CentOS/Fedora:**
```bash
sudo dnf groupinstall "Development Tools" -y
sudo dnf install curl wget git -y
```

### 4. Clone Repository

```bash
git clone <repo-url>
cd sql-assistant-with-local-llm
```

### 5. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 6. Install Dependencies

**For CPU-only:**
```bash
pip install -r requirements-macos.txt
```

**For GPU (NVIDIA CUDA):**
```bash
pip install -r requirements-linux.txt
```

**Using uv (faster):**
```bash
pip install uv
uv pip install -r requirements-linux.txt  # GPU version
# or
uv pip install -r requirements-macos.txt  # CPU-only
```

### 7. (Optional) Install CUDA Toolkit

For GPU acceleration, install NVIDIA CUDA:

```bash
# Check NVIDIA GPU
nvidia-smi

# If no output, install GPU drivers
# Follow: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/

# Verify CUDA installation
nvcc --version
```

### 8. Download LLM Model

```bash
mkdir -p models

# phi-3-sql (Recommended)
curl -L https://huggingface.co/omeryentur/phi-3-sql/resolve/main/phi-3-sql.Q4_K_M.gguf \
  -o models/phi-3-sql.Q4_K_M.gguf

# Or nsql-llama-2
# curl -L https://huggingface.co/TheBloke/nsql-llama-2-7B-GGUF/resolve/main/nsql-llama-2-7b.Q5_K_M.gguf \
#   -o models/nsql-llama-2-7b.Q5_K_M.gguf
```

### 9. Configure Application

Edit `config.yaml`:

```yaml
llm:
  model_path: "models/phi-3-sql.Q4_K_M.gguf"
  model_type: "mistral"
  gpu_layers: 30  # Increase if you have GPU
  temperature: 0.1

database:
  path: "students_data_multi_table.db"
  type: "sqlite"

security:
  max_queries_per_minute: 100
  max_result_rows: 10000
  enable_guardrails: true
```

### 10. (Optional) Create Sample Database

```bash
python load_sql_database.py
```

### 11. Run the Application

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## Troubleshooting

### Issue: "cuda runtime error"

**Solution:**
```bash
# Verify CUDA is installed
nvidia-smi
nvcc --version

# Reinstall torch with correct CUDA version
pip uninstall torch -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "Insufficient GPU memory"

**Solution:**
Reduce GPU layers in `config.yaml`:
```yaml
llm:
  gpu_layers: 10  # Reduce from 30
```

### Issue: Permission denied error

**Solution:**
```bash
# Fix permissions
chmod +x *.py
chmod -R 755 models/
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port 8501
sudo lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run app.py --server.port 8502
```

---

## Performance Optimization

### GPU Setup

```bash
# Check GPU
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Monitor GPU usage during inference
watch -n 1 nvidia-smi
```

### CPU Setup

For high-performance CPU inference:

```bash
# Install MKL for faster linear algebra
pip install mkl

# Set environment variables
export MKL_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export OMP_NUM_THREADS=8
export VECLIB_MAXIMUM_THREADS=8
```

### Model Selection

| Setup | Recommended Model | GPU Layers | Speed |
|-------|------------------|-----------|-------|
| CPU-only | phi-3-sql Q4_K_M | 0 | Slow |
| GPU 4GB | phi-3-sql Q4_K_M | 10 | Medium |
| GPU 6GB+ | phi-3-sql Q5_K_M | 20 | Fast |
| GPU 12GB+ | nsql-llama-2 Q5_K_M | 30+ | Very Fast |

---

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t sql-assistant .

# Run container
docker run -p 8501:8501 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  sql-assistant

# Run with GPU support
docker run --gpus all -p 8501:8501 \
  -v $(pwd)/models:/app/models \
  sql-assistant
```

### Using Docker Compose

```bash
# Run
docker-compose up --build

# With GPU
docker-compose -f docker-compose.gpu.yml up --build
```

---

## Systemd Service (Optional)

Create a systemd service for automatic startup:

```bash
sudo cat > /etc/systemd/system/sql-assistant.service << EOF
[Unit]
Description=SQL Assistant Streamlit App
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/streamlit run app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable sql-assistant
sudo systemctl start sql-assistant

# Check status
sudo systemctl status sql-assistant

# View logs
sudo journalctl -u sql-assistant -f
```

---

## Production Deployment

### Using systemd + Nginx

```bash
# Install Nginx
sudo apt-get install nginx -y

# Create Nginx config
sudo cat > /etc/nginx/sites-available/sql-assistant << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/sql-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## Monitoring

### System Resources

```bash
# Monitor system
top
htop  # Install: sudo apt-get install htop

# Monitor disk
df -h
du -sh .

# Monitor network
iftop  # Install: sudo apt-get install iftop
```

### Application Logs

```bash
# View Streamlit logs
tail -f ~/.streamlit/logs/

# View system service logs
sudo journalctl -u sql-assistant -f
```

---

## Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements-linux.txt

# Restart service
sudo systemctl restart sql-assistant
```

---

## Uninstalling

```bash
# Stop service
sudo systemctl stop sql-assistant
sudo systemctl disable sql-assistant
sudo systemctl daemon-reload

# Remove service file
sudo rm /etc/systemd/system/sql-assistant.service

# Remove installation
cd ..
rm -rf sql-assistant-with-local-llm
```

---

## Additional Resources

- [PyTorch CUDA Installation](https://pytorch.org/get-started/locally/)
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [ctransformers GitHub](https://github.com/marella/ctransformers)

---

**Last Updated**: January 2, 2026
