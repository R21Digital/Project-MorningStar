# 🚀 MS11 Live Testing Guide

This guide will help you deploy and test MS11 in a live environment for the first time.

## 📋 Prerequisites

Before starting live testing, ensure you have:

- ✅ Python 3.11+ installed
- ✅ Docker and Docker Compose installed
- ✅ Git repository cloned
- ✅ Valid MS11 license (or demo mode)
- ✅ Target SWG server access

## 🏗️ Quick Deployment

### 1. Automated Deployment

```bash
# Deploy to staging environment
python scripts/deploy_ms11.py --environment staging

# Deploy to production (use with caution)
python scripts/deploy_ms11.py --environment production
```

### 2. Manual Docker Deployment

```bash
# Build the Docker image
docker build -t ms11:latest .

# Start the services
docker-compose up -d

# Check status
docker-compose ps
```

## 🧪 Live Testing Checklist

### Phase 1: Environment Setup

- [ ] **Docker containers running**
  ```bash
  docker-compose ps
  # Should show ms11-app and ms11-xvfb as "Up"
  ```

- [ ] **Environment variables set**
  ```bash
  # Set your license key
  export ANDROID_MS11_LICENSE=your_license_key
  ```

- [ ] **Character profile configured**
  ```bash
  # Create/edit your profile in profiles/runtime/
  cp profiles/runtime/default.json profiles/runtime/my_character.json
  # Edit the profile with your character details
  ```

### Phase 2: Core Functionality Tests

- [ ] **Basic system test**
  ```bash
  docker-compose exec ms11-app python test_basic.py
  ```

- [ ] **OCR functionality test**
  ```bash
  docker-compose exec ms11-app python -c "
  import pytesseract
  import cv2
  print('OCR dependencies working')
  "
  ```

- [ ] **Vision system test**
  ```bash
  docker-compose exec ms11-app python -c "
  import pyautogui
  print('Vision system ready')
  "
  ```

### Phase 3: Mode Testing

Test each MS11 mode individually:

#### Quest Mode
```bash
docker-compose exec ms11-app python src/main.py --mode quest --profile my_character
```

#### Combat Mode
```bash
docker-compose exec ms11-app python src/main.py --mode combat --profile my_character
```

#### Medic Mode
```bash
docker-compose exec ms11-app python src/main.py --mode medic --profile my_character
```

#### Crafting Mode
```bash
docker-compose exec ms11-app python src/main.py --mode crafting --profile my_character
```

### Phase 4: Integration Testing

- [ ] **Discord integration** (if enabled)
- [ ] **Session monitoring**
- [ ] **Logging and reporting**
- [ ] **Performance monitoring**

## 📊 Monitoring & Debugging

### View Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ms11-app

# View recent logs
docker-compose logs --tail=100 ms11-app
```

### Health Checks
```bash
# Check container health
docker-compose ps

# Check application health
docker-compose exec ms11-app python -c "
import sys
sys.exit(0)
"
```

### Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Check disk usage
docker-compose exec ms11-app df -h
```

## 🔧 Troubleshooting

### Common Issues

#### 1. OCR Not Working
```bash
# Check Tesseract installation
docker-compose exec ms11-app tesseract --version

# Test OCR with sample image
docker-compose exec ms11-app python -c "
import pytesseract
from PIL import Image
# Test OCR functionality
"
```

#### 2. Vision System Issues
```bash
# Check display setup
docker-compose exec ms11-app echo $DISPLAY

# Test screen capture
docker-compose exec ms11-app python -c "
import pyautogui
print('Screen size:', pyautogui.size())
"
```

#### 3. Mode-Specific Issues
```bash
# Test individual mode imports
docker-compose exec ms11-app python -c "
try:
    from android_ms11.modes import quest_mode
    print('Quest mode available')
except ImportError as e:
    print('Quest mode not available:', e)
"
```

### Debug Mode
```bash
# Run with debug logging
docker-compose exec ms11-app python src/main.py --debug --profile my_character
```

## 📈 Performance Optimization

### Resource Limits
```yaml
# Add to docker-compose.yml
services:
  ms11:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### Monitoring Setup
```bash
# Install monitoring tools
docker-compose exec ms11-app pip install psutil

# Monitor performance
docker-compose exec ms11-app python -c "
import psutil
print('CPU:', psutil.cpu_percent())
print('Memory:', psutil.virtual_memory().percent)
"
```

## 🚨 Safety Guidelines

### Before Live Testing

1. **Backup your character data**
2. **Test in a safe area first**
3. **Have emergency stop procedures ready**
4. **Monitor system resources**
5. **Keep logs for analysis**

### Emergency Procedures

```bash
# Stop all MS11 processes
docker-compose down

# Emergency stop (force kill)
docker-compose kill

# Restart safely
docker-compose up -d
```

## 📝 Testing Report Template

After completing live testing, document your findings:

```markdown
# MS11 Live Testing Report

## Test Environment
- Date: [Date]
- Environment: [Staging/Production]
- Character: [Character Name]
- Server: [Server Name]

## Test Results

### Core Functionality
- [ ] Basic system startup
- [ ] OCR functionality
- [ ] Vision system
- [ ] Mode switching

### Individual Modes
- [ ] Quest mode
- [ ] Combat mode
- [ ] Medic mode
- [ ] Crafting mode
- [ ] Other modes...

### Performance
- CPU usage: [%]
- Memory usage: [%]
- Response time: [ms]

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
1. [Recommendation]
2. [Recommendation]
```

## 🎯 Next Steps

After successful live testing:

1. **Document any issues** in the testing report
2. **Optimize performance** based on findings
3. **Update configurations** for production use
4. **Set up monitoring** for long-term use
5. **Plan regular testing** schedules

## 📞 Support

If you encounter issues during live testing:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Test individual components
4. Contact the development team with detailed error reports

---

**Remember**: Always test in a controlled environment first, and never run MS11 on characters you're not willing to risk.
