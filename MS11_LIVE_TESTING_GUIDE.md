# 🚀 MS11 Live Testing Guide - Complete Instructions

## 🎯 **What is Live Testing?**

Live testing means running MS11 in a real SWG environment to verify it works as expected. This involves:
- Starting MS11 with a specific mode and profile
- Monitoring its behavior in real-time
- Verifying it performs the intended functions
- Testing for any issues or unexpected behavior

## 🛡️ **Safety Guidelines - READ FIRST!**

### **Before Starting Live Testing:**
- ✅ **Test in a safe area** (low-level zones, away from PvP)
- ✅ **Start with short sessions** (5-10 minutes first)
- ✅ **Have an emergency stop method** (Ctrl+C or close the terminal)
- ✅ **Monitor closely** for the first few runs
- ✅ **Use demo mode** for initial testing
- ✅ **Backup your character** if possible

### **Recommended Testing Order:**
1. **Quest Mode** (safest, most predictable)
2. **Medic Mode** (support role, low risk)
3. **Crafting Mode** (stationary, safe)
4. **Combat Mode** (higher risk, test carefully)
5. **Other Modes** (as needed)

## 🚀 **Method 1: Interface-Based Live Testing (Recommended)**

### **Step 1: Start the MS11 Interface**
```bash
python scripts/ms11_interface.py
```

### **Step 2: Configure Your Environment**
1. Select **"System Management"** → **"Configure Environment"**
2. Enter your license key (or 'demo' for demo mode)
3. Set any other environment variables needed

### **Step 3: Select Your Profile**
1. Select **"Profile Management"** → **"Select Profile"**
2. Choose from available profiles:
   - `default` - General purpose (recommended for first test)
   - `questing` - Quest-focused
   - `medic` - Healing/support
   - `crafting` - Crafting activities
   - `grinding` - Combat/grinding

### **Step 4: Choose Your Mode**
1. Select **"Mode Control"** → Choose a mode:
   - **Quest Mode** (safest for first test)
   - **Combat Mode** (test carefully)
   - **Medic Mode** (support role)
   - **Crafting Mode** (stationary)
   - **Other Modes** (bounty, entertainer, etc.)

### **Step 5: Start Live Testing**
1. Select **"Session Management"** → **"Start New Session"**
2. Monitor the session through the interface
3. Watch for any issues or unexpected behavior
4. Use **"Stop Current Session"** when done

## 🖥️ **Method 2: Direct Command Line Live Testing**

### **Quick Start Commands:**

```bash
# Set Python path for Windows
$env:PYTHONPATH = ".;$env:PYTHONPATH"

# Test Quest Mode (Safest)
python src/main.py --mode quest --profile default

# Test Combat Mode
python src/main.py --mode combat --profile default

# Test Medic Mode
python src/main.py --mode medic --profile default

# Test Crafting Mode
python src/main.py --mode crafting --profile default

# Test with different profiles
python src/main.py --mode quest --profile questing
python src/main.py --mode medic --profile medic
```

### **Advanced Options:**
```bash
# Run with smart mode selection
python src/main.py --smart --profile default

# Run in continuous loop
python src/main.py --mode quest --profile default --loop

# Run with specific settings
python src/main.py --mode quest --profile default --rest 30
```

## 🌐 **Method 3: Web Dashboard Live Testing**

### **Step 1: Start Web Dashboard**
```bash
$env:PYTHONPATH = ".;$env:PYTHONPATH"; python dashboard/app.py
```

### **Step 2: Access Dashboard**
- Open your browser
- Go to: `http://localhost:5000/ms11`
- Login with your credentials

### **Step 3: Monitor Live Sessions**
- View real-time session status
- Monitor performance metrics
- Check logs and alerts
- Manage profiles and modes

## 📋 **Live Testing Checklist**

### **Before Starting:**
- [ ] SWG client is running and logged in
- [ ] Character is in a safe location
- [ ] Emergency stop method is ready (Ctrl+C)
- [ ] Monitoring interface is open
- [ ] Test session planned (5-10 minutes)

### **During Testing:**
- [ ] Watch for expected behavior
- [ ] Monitor for errors or crashes
- [ ] Check if modes execute correctly
- [ ] Verify performance is acceptable
- [ ] Note any unexpected behavior

### **After Testing:**
- [ ] Stop the session cleanly
- [ ] Check logs for any issues
- [ ] Review performance metrics
- [ ] Document any problems found
- [ ] Plan next test session

## 🎯 **Recommended Live Testing Scenarios**

### **Scenario 1: First-Time Testing (5 minutes)**
```bash
# Start with quest mode in a safe area
$env:PYTHONPATH = ".;$env:PYTHONPATH"; python src/main.py --mode quest --profile default
```
**What to expect:**
- MS11 will load and initialize
- It may attempt to find quests
- It will try to train skills
- Monitor for any crashes or errors

### **Scenario 2: Combat Testing (10 minutes)**
```bash
# Test combat mode in a low-level area
$env:PYTHONPATH = ".;$env:PYTHONPATH"; python src/main.py --mode combat --profile default
```
**What to expect:**
- MS11 will scan for targets
- It may attempt combat actions
- Monitor health and safety
- Watch for proper target selection

### **Scenario 3: Medic Testing (10 minutes)**
```bash
# Test medic mode in a populated area
$env:PYTHONPATH = ".;$env:PYTHONPATH"; python src/main.py --mode medic --profile default
```
**What to expect:**
- MS11 will look for players to heal
- It may attempt healing actions
- Monitor for proper target selection
- Watch for buff applications

### **Scenario 4: Crafting Testing (15 minutes)**
```bash
# Test crafting mode at a crafting station
$env:PYTHONPATH = ".;$env:PYTHONPATH"; python src/main.py --mode crafting --profile default
```
**What to expect:**
- MS11 will attempt crafting actions
- It may manage inventory
- Monitor for proper station usage
- Watch for crafting success/failure

## 📊 **Monitoring During Live Testing**

### **What to Watch For:**

#### **✅ Good Signs:**
- MS11 starts without errors
- Modes execute their intended functions
- No crashes or freezes
- Performance is acceptable
- Logs show normal activity

#### **⚠️ Warning Signs:**
- Frequent crashes or errors
- Unexpected behavior
- Poor performance
- Missing functionality
- License or authentication issues

#### **❌ Stop Immediately If:**
- Character is in danger
- Unexpected combat engagement
- System becomes unresponsive
- Critical errors occur
- Performance degrades significantly

## 🔧 **Troubleshooting Live Testing Issues**

### **Common Issues and Solutions:**

#### **1. "Module not found" errors:**
```bash
# Fix Python path
$env:PYTHONPATH = ".;$env:PYTHONPATH"
```

#### **2. License issues:**
```bash
# Set demo mode
$env:ANDROID_MS11_LICENSE = "demo"
```

#### **3. Profile not found:**
```bash
# Use default profile
python src/main.py --mode quest --profile default
```

#### **4. Mode not working:**
```bash
# Check system validation first
python scripts/quick_test_ms11.py
```

#### **5. Performance issues:**
- Close other applications
- Reduce graphics settings
- Use shorter test sessions
- Monitor system resources

## 📈 **Success Metrics for Live Testing**

### **✅ System is Working When:**
- MS11 starts and stops cleanly
- Modes execute their intended functions
- No crashes or unexpected behavior
- Performance is acceptable
- Monitoring works properly

### **✅ Ready for Production When:**
- All modes tested successfully
- No critical issues found
- Performance meets requirements
- Safety measures confirmed
- Monitoring systems operational

## 🎉 **Quick Start Commands**

```bash
# 1. System Check (Always do this first)
python scripts/quick_test_ms11.py

# 2. Start Interface (Recommended)
python scripts/ms11_interface.py

# 3. Direct Testing (Quick test)
$env:PYTHONPATH = ".;$env:PYTHONPATH"; python src/main.py --mode quest --profile default

# 4. Web Dashboard (For monitoring)
$env:PYTHONPATH = ".;$env:PYTHONPATH"; python dashboard/app.py

# 5. Emergency Stop
# Press Ctrl+C in the terminal
```

## 🚀 **Ready to Start Live Testing?**

**Choose your method and get started:**

1. **Interface Method** (Recommended for beginners):
   ```bash
   python scripts/ms11_interface.py
   ```

2. **Direct Command** (Quick testing):
   ```bash
   $env:PYTHONPATH = ".;$env:PYTHONPATH"; python src/main.py --mode quest --profile default
   ```

3. **Web Dashboard** (For monitoring):
   ```bash
   $env:PYTHONPATH = ".;$env:PYTHONPATH"; python dashboard/app.py
   ```

**MS11 is ready for live testing! Start with a 5-minute quest mode test and monitor closely. 🎯**
