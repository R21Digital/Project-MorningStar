# 🚀 MS11 Setup Guide - Updated for Current State

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform Support](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/project-morningstar/Project-MorningStar)
[![Tests Passing](https://img.shields.io/badge/tests-6%2F9%20passing-yellow.svg)](https://github.com/project-morningstar/Project-MorningStar/actions)

This guide reflects the current state of MS11 with all recent improvements and fixes applied.

## 📋 Prerequisites

### **System Requirements**
- **Python**: 3.11, 3.12, or 3.13 (3.13 recommended)
- **Operating System**: Windows 10/11 or Linux (Ubuntu/Debian preferred)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Display**: 1920x1080 minimum resolution

### **Required System Dependencies**

#### **Windows**
```powershell
# Install Tesseract OCR via Chocolatey
choco install tesseract

# OR download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

#### **Linux (Ubuntu/Debian)**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr xvfb libx11-dev libxext-dev
```

## 🔧 Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/project-morningstar/Project-MorningStar.git
cd Project-MorningStar
```

### **2. Set Up Python Environment**
```bash
# Install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### **3. Verify Installation**
```bash
# Run the comprehensive system test
python scripts/quick_test_ms11.py
```

**Expected Output:**
```
Test Results: 6/9 tests passed
[PASS] Python 3.13.2 - Compatible
[PASS] Dependencies - All installed
[PASS] Directory Structure - Complete  
[PASS] Configuration Files - Present
[PASS] Vision Components - Working
[PASS] Screen capture working (size: 2560x1440)
```

## ⚙️ Configuration

### **1. Environment Setup**
```bash
# Set license key (optional - will use demo mode if not set)
export ANDROID_MS11_LICENSE=demo

# Windows users use:
set ANDROID_MS11_LICENSE=demo
```

### **2. Profile Configuration**
Default profiles are available in `profiles/runtime/`:
- `default.json` - General purpose profile
- `questing.json` - Quest-focused configuration
- `medic.json` - Healing/support profile
- `crafting.json` - Crafting activities
- `grinding.json` - Combat/grinding

## 🚀 Running MS11

### **Quick Start Interface (Recommended)**
```bash
python scripts/ms11_interface.py
```
This provides a menu-driven interface for all MS11 functionality.

### **Web Dashboard**
```bash
python dashboard/app.py
# Visit: http://localhost:5000/ms11
```

### **Direct Command Line**
```bash
# Run with specific mode and profile
python src/main.py --mode quest --profile default

# Available modes: quest, combat, medic, crafting, bounty, entertainer, 
#                  rls, special-goals, whisper, support, follow, dancer
```

### **GUI Interface**
```bash
python scripts/ms11_gui.py
```

## 🧪 Testing & Validation

### **Quick System Test**
```bash
python scripts/quick_test_ms11.py
```

### **Run Full Test Suite**
```bash
# Run all tests
pytest tests/test_ci_sanity.py -v

# Run with coverage
pytest --cov=src tests/test_ci_sanity.py
```

### **Platform-Specific Testing**
```bash
# Linux - skip Windows-only tests
pytest -m "not windows_only"

# Windows - skip Linux-only tests  
pytest -m "not linux_skip"
```

## 🛠️ Development Setup

### **Development Dependencies**
```bash
pip install -r requirements-dev.txt
```

### **Pre-commit Hooks**
```bash
pre-commit install
```

### **Code Quality Checks**
```bash
# Security scan
bandit -r src/

# Type checking (if using mypy)
mypy src/

# Linting
flake8 src/
```

## 📊 Current System Status

### **✅ What's Working**
- ✅ **Python 3.11-3.13** compatibility
- ✅ **Cross-platform** support (Windows + Linux)
- ✅ **Enhanced CI/CD** with matrix testing
- ✅ **Improved error handling** with structured logging
- ✅ **Type safety** with comprehensive type hints
- ✅ **Vision components** (screen capture, OCR ready)
- ✅ **Multiple interfaces** (CLI, GUI, Web, API)

### **⚠️ Known Issues**
- ⚠️ **Tesseract OCR** may need PATH configuration
- ⚠️ **Core module imports** - some relative import issues on fresh installs
- ⚠️ **License validation** - demo mode works, full licensing may need setup

### **📈 Test Results**
Current test suite passes **6 out of 9 tests**:
- ✅ Python version compatibility
- ✅ All Python dependencies installed
- ✅ Directory structure complete
- ✅ Configuration files present  
- ✅ Vision libraries working
- ✅ Screen capture functional
- ⚠️ System dependencies (Tesseract)
- ⚠️ Core module imports
- ⚠️ Main script execution

## 🔧 Troubleshooting

### **Common Issues**

#### **"tesseract not found" Error**
```bash
# Windows: Add to PATH or reinstall
choco install tesseract

# Linux: Install package
sudo apt-get install tesseract-ocr

# Verify installation
tesseract --version
```

#### **Import Errors**
```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)/core:$(pwd)"

# Windows
set PYTHONPATH=%PYTHONPATH%;%CD%\src;%CD%\core;%CD%
```

#### **Permission Issues (Linux)**
```bash
# Make scripts executable
chmod +x scripts/*.py

# Install xvfb for headless GUI testing
sudo apt-get install xvfb
```

### **Getting Help**
1. **Check logs**: `logs/ms11.log` for detailed error information
2. **Run diagnostics**: `python scripts/quick_test_ms11.py`
3. **Use the interface**: `python scripts/ms11_interface.py` for guided setup

## 📚 Next Steps

### **For First-Time Users**
1. Run the quick test to verify setup: `python scripts/quick_test_ms11.py`
2. Start the interface: `python scripts/ms11_interface.py`
3. Create/configure your profile
4. Test with quest mode: `python src/main.py --mode quest --profile default`

### **For Developers**
1. Set up development environment with all dependencies
2. Run full test suite: `pytest`
3. Check CI/CD status on GitHub Actions
4. Review code quality with security scans

### **For Advanced Users**
1. Deploy with Docker: `docker-compose up -d`
2. Set up web dashboard: `python dashboard/app.py`
3. Configure production environment
4. Set up monitoring and logging

---

## 📞 Support

- 📖 **Documentation**: See `docs/` directory for detailed guides
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Community**: Join our Discord server
- 🤝 **Contributing**: See `CONTRIBUTING.md` for guidelines

**MS11 is ready for testing and development!** 🎉