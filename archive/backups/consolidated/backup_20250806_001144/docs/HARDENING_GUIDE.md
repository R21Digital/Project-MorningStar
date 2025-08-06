# MS11 Hardening Guide

## Overview
This guide provides comprehensive instructions for hardening the MS11 system against detection by game servers and anti-cheat systems. It covers all aspects of security, from basic configuration to advanced anti-detection techniques.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Detection Surfaces](#detection-surfaces)
3. [Configuration Hardening](#configuration-hardening)
4. [Behavior Hardening](#behavior-hardening)
5. [Network Hardening](#network-hardening)
6. [System Hardening](#system-hardening)
7. [Monitoring & Auditing](#monitoring--auditing)
8. [Emergency Procedures](#emergency-procedures)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Immediate Actions Required
1. **Enable Safety Defaults**
   ```bash
   # Verify safety defaults are enabled
   python -c "from safety.redteam.audit_runner import get_redteam_auditor; auditor = get_redteam_auditor(); print('Safety defaults:', auditor._check_safety_defaults())"
   ```

2. **Run Initial Audit**
   ```bash
   # Run comprehensive audit
   python -c "from safety.redteam.audit_runner import get_redteam_auditor; auditor = get_redteam_auditor(); report = auditor.run_full_audit(); print('Audit completed:', report.overall_risk_level.value)"
   ```

3. **Apply Critical Fixes**
   - Enable session caps
   - Enable humanization features
   - Enable anti-pattern detection
   - Configure random delays

### Critical Configuration Changes
```json
{
  "safety_defaults": {
    "session_caps": {"enabled": true},
    "humanization": {"enabled": true},
    "anti_patterns": {"enabled": true}
  }
}
```

## Detection Surfaces

### 1. Process Names & Window Titles

#### Risk Level: HIGH
**Problem**: Suspicious process names can immediately flag automation.

**Solution**:
```python
# Use generic process names
process_names = [
    "swg_client.exe",
    "starwars_galaxies.exe", 
    "game_client.exe"
]

# Avoid these terms:
avoided_terms = [
    "bot", "auto", "macro", "script", "hack", "cheat",
    "automation", "program", "tool", "helper", "ms11"
]
```

**Implementation**:
1. Rename any processes containing suspicious terms
2. Use generic window titles
3. Randomize process names if possible
4. Monitor for consistent naming patterns

### 2. Macro Cadence & Timing

#### Risk Level: CRITICAL
**Problem**: Perfect timing patterns are the most obvious bot signature.

**Solution**:
```python
# Implement human-like timing
import random
import time

def humanized_delay(base_delay=1.0):
    """Add human-like variance to delays."""
    variance = random.uniform(0.2, 2.0)
    return base_delay * variance

def random_action_delay():
    """Random delay between actions."""
    return random.uniform(0.1, 2.0)

# Usage
time.sleep(humanized_delay(1.0))
```

**Requirements**:
- Minimum delay: 50ms between actions
- Maximum delay: 2000ms for human-like patterns
- Variance threshold: >10% for timing patterns
- No perfect repetition beyond 3-5 identical actions

### 3. Input Timing Patterns

#### Risk Level: CRITICAL
**Problem**: Machine-perfect input timing is easily detected.

**Solution**:
```python
# Human-like input timing
def humanized_click():
    """Simulate human-like click timing."""
    pre_click_delay = random.uniform(0.05, 0.2)
    click_duration = random.uniform(0.01, 0.05)
    post_click_delay = random.uniform(0.05, 0.3)
    
    time.sleep(pre_click_delay)
    # Perform click
    time.sleep(click_duration)
    time.sleep(post_click_delay)

def humanized_movement():
    """Simulate human-like mouse movement."""
    movement_time = random.uniform(0.1, 0.5)
    # Implement curved movement paths
    # Add acceleration/deceleration
```

**Human-Like Patterns**:
- Response time variance: 200-800ms
- Click timing variance: 50-200ms
- Movement timing variance: 100-500ms
- No identical timing patterns

### 4. Session Length & Patterns

#### Risk Level: MEDIUM
**Problem**: Unrealistic session lengths indicate automation.

**Solution**:
```python
# Session management
class SessionManager:
    def __init__(self):
        self.max_session_hours = 6
        self.min_break_hours = 2
        self.session_variance = True
    
    def should_start_session(self):
        """Check if it's safe to start a new session."""
        # Implement session variance logic
        pass
    
    def enforce_session_caps(self):
        """Enforce session duration limits."""
        # Implement session caps
        pass
```

**Session Requirements**:
- Maximum session: 6 hours
- Minimum break: 2 hours between sessions
- Session variance: ±2 hours
- No 24/7 operation patterns

## Configuration Hardening

### 1. Safety Defaults Configuration

#### Critical Settings
```json
{
  "session_management": {
    "session_caps": {
      "enabled": true,
      "max_daily_hours": 8,
      "max_weekly_hours": 40,
      "max_session_hours": 6,
      "mandatory_breaks": true
    }
  },
  "humanization": {
    "enabled": true,
    "random_delays": {
      "enabled": true,
      "min_delay_ms": 50,
      "max_delay_ms": 2000
    }
  },
  "anti_patterns": {
    "enabled": true,
    "repetitive_actions": {
      "enabled": true,
      "max_consecutive_identical": 3
    }
  }
}
```

#### Enforcement Settings
```json
{
  "enforcement": {
    "enabled": true,
    "strict_mode": {
      "enabled": true,
      "block_unsafe_operations": true,
      "require_safety_compliance": true
    }
  }
}
```

### 2. Detection Surface Configuration

#### Process & Window Title Security
```json
{
  "detection_surfaces": {
    "process_names": {
      "enabled": true,
      "suspicious_patterns": [
        "bot", "auto", "macro", "script", "hack", "cheat"
      ],
      "whitelist": ["swg", "starwars", "galaxies", "client"],
      "enforce_generic_names": true
    },
    "window_titles": {
      "enabled": true,
      "suspicious_patterns": [
        "bot", "auto", "macro", "script", "hack", "cheat"
      ],
      "whitelist": ["star wars galaxies", "swg", "galaxies"],
      "enforce_generic_titles": true
    }
  }
}
```

#### Timing Security
```json
{
  "detection_surfaces": {
    "macro_cadence": {
      "enabled": true,
      "max_repetition": 3,
      "min_variance": 0.15,
      "enforce_timing_variance": true
    },
    "input_timing": {
      "enabled": true,
      "min_delay_ms": 50,
      "max_delay_ms": 2000,
      "human_like_patterns": true
    }
  }
}
```

## Behavior Hardening

### 1. Humanization Features

#### Emote System
```python
# Emote system implementation
class EmoteSystem:
    def __init__(self):
        self.emotes = [
            {"command": "/sit", "probability": 0.4},
            {"command": "/mood", "probability": 0.2},
            {"command": "/dance", "probability": 0.1},
            {"command": "/wave", "probability": 0.15},
            {"command": "/nod", "probability": 0.1},
            {"command": "/shrug", "probability": 0.05}
        ]
    
    def perform_random_emote(self):
        """Perform a random emote based on probability."""
        if random.random() < 0.3:  # 30% chance per check
            emote = random.choices(
                self.emotes, 
                weights=[e["probability"] for e in self.emotes]
            )[0]
            return emote["command"]
        return None
```

#### Idle Behavior
```python
# Idle behavior system
class IdleBehavior:
    def __init__(self):
        self.idle_actions = [
            {"action": "craft", "probability": 0.3},
            {"action": "socialize", "probability": 0.2},
            {"action": "explore", "probability": 0.25},
            {"action": "rest", "probability": 0.25}
        ]
    
    def perform_idle_action(self):
        """Perform a random idle action."""
        if random.random() < 0.6:  # 60% chance
            action = random.choices(
                self.idle_actions,
                weights=[a["probability"] for a in self.idle_actions]
            )[0]
            return action["action"]
        return None
```

### 2. Anti-Pattern Detection

#### Repetitive Action Detection
```python
# Anti-pattern detection
class AntiPatternDetector:
    def __init__(self):
        self.action_history = []
        self.max_consecutive_identical = 3
    
    def check_repetitive_actions(self, action):
        """Check for repetitive action patterns."""
        self.action_history.append(action)
        
        # Keep only recent history
        if len(self.action_history) > 10:
            self.action_history = self.action_history[-10:]
        
        # Check for repetitive patterns
        if len(self.action_history) >= self.max_consecutive_identical:
            recent_actions = self.action_history[-self.max_consecutive_identical:]
            if len(set(recent_actions)) == 1:
                return False  # Repetitive pattern detected
        
        return True
```

#### Perfect Timing Detection
```python
# Perfect timing detection
class TimingDetector:
    def __init__(self):
        self.timing_history = []
        self.max_identical_timing = 2
        self.min_variance_required = 0.1
    
    def check_timing_variance(self, timing):
        """Check for timing variance."""
        self.timing_history.append(timing)
        
        if len(self.timing_history) >= self.max_identical_timing:
            recent_timings = self.timing_history[-self.max_identical_timing:]
            if len(set(recent_timings)) == 1:
                return False  # Perfect timing detected
        
        return True
```

## Network Hardening

### 1. Network Signature Randomization

#### Packet Timing Variance
```python
# Network timing variance
def randomize_network_timing(base_delay):
    """Add variance to network timing."""
    variance = random.uniform(0.85, 1.15)  # ±15%
    return base_delay * variance
```

#### Connection Pattern Variance
```python
# Connection pattern variance
def randomize_connection_pattern():
    """Randomize connection patterns."""
    # Vary connection timing
    # Randomize packet sizes
    # Add connection delays
    pass
```

### 2. Request Frequency Control

#### Rate Limiting
```python
# Rate limiting implementation
class RateLimiter:
    def __init__(self):
        self.request_history = []
        self.max_requests_per_minute = 60
    
    def check_rate_limit(self):
        """Check if request is within rate limits."""
        current_time = time.time()
        
        # Remove old requests
        self.request_history = [
            req_time for req_time in self.request_history
            if current_time - req_time < 60
        ]
        
        if len(self.request_history) >= self.max_requests_per_minute:
            return False
        
        self.request_history.append(current_time)
        return True
```

## System Hardening

### 1. Memory Pattern Variance

#### Memory Usage Randomization
```python
# Memory usage variance
def randomize_memory_usage():
    """Add variance to memory usage patterns."""
    # Vary memory allocation timing
    # Randomize memory access patterns
    # Add memory usage variance
    pass
```

### 2. File Access Pattern Randomization

#### File System Hardening
```python
# File access randomization
def randomize_file_access():
    """Randomize file access patterns."""
    # Vary file read/write timing
    # Randomize file access patterns
    # Add file system variance
    pass
```

## Monitoring & Auditing

### 1. Real-Time Monitoring

#### Continuous Monitoring
```python
# Real-time monitoring
class SafetyMonitor:
    def __init__(self):
        self.check_interval = 30  # seconds
        self.alert_threshold = 0.8
    
    def start_monitoring(self):
        """Start continuous monitoring."""
        while True:
            self.check_safety_status()
            time.sleep(self.check_interval)
    
    def check_safety_status(self):
        """Check current safety status."""
        # Implement safety checks
        pass
```

### 2. Audit Scheduling

#### Automated Audits
```python
# Audit scheduling
class AuditScheduler:
    def __init__(self):
        self.audit_interval = 3600  # 1 hour
        self.last_audit = 0
    
    def schedule_audit(self):
        """Schedule regular audits."""
        current_time = time.time()
        if current_time - self.last_audit >= self.audit_interval:
            self.run_audit()
            self.last_audit = current_time
    
    def run_audit(self):
        """Run comprehensive audit."""
        from safety.redteam.audit_runner import get_redteam_auditor
        auditor = get_redteam_auditor()
        report = auditor.run_full_audit()
        return report
```

### 3. Alert System

#### Alert Configuration
```python
# Alert system
class AlertSystem:
    def __init__(self):
        self.critical_alerts = True
        self.warning_alerts = True
        self.info_alerts = False
    
    def send_alert(self, level, message):
        """Send alert based on level."""
        if level == "critical" and self.critical_alerts:
            self.send_critical_alert(message)
        elif level == "warning" and self.warning_alerts:
            self.send_warning_alert(message)
        elif level == "info" and self.info_alerts:
            self.send_info_alert(message)
    
    def send_critical_alert(self, message):
        """Send critical alert."""
        # Implement critical alert logic
        print(f"CRITICAL: {message}")
    
    def send_warning_alert(self, message):
        """Send warning alert."""
        # Implement warning alert logic
        print(f"WARNING: {message}")
```

## Emergency Procedures

### 1. Immediate Response

#### Critical Detection Response
```python
# Emergency response
class EmergencyResponse:
    def __init__(self):
        self.emergency_procedures = {
            "critical_detection": self.handle_critical_detection,
            "suspicious_activity": self.handle_suspicious_activity,
            "system_compromise": self.handle_system_compromise
        }
    
    def handle_critical_detection(self):
        """Handle critical detection event."""
        # Immediate shutdown
        # Clear logs
        # Change patterns
        # Notify administrator
        pass
    
    def handle_suspicious_activity(self):
        """Handle suspicious activity."""
        # Reduce activity
        # Increase randomization
        # Monitor closely
        pass
    
    def handle_system_compromise(self):
        """Handle system compromise."""
        # Complete shutdown
        # Secure all data
        # Change all patterns
        # Full system audit
        pass
```

### 2. Pattern Reset

#### Emergency Pattern Reset
```python
# Pattern reset
class PatternReset:
    def __init__(self):
        self.reset_procedures = [
            "clear_action_history",
            "reset_timing_patterns",
            "change_behavior_patterns",
            "update_session_patterns"
        ]
    
    def emergency_reset(self):
        """Perform emergency pattern reset."""
        for procedure in self.reset_procedures:
            self.execute_procedure(procedure)
    
    def execute_procedure(self, procedure):
        """Execute specific reset procedure."""
        if procedure == "clear_action_history":
            self.clear_action_history()
        elif procedure == "reset_timing_patterns":
            self.reset_timing_patterns()
        # ... other procedures
```

## Best Practices

### 1. Configuration Management

#### Secure Defaults
- Always enable safety defaults
- Use strict enforcement mode
- Enable all humanization features
- Configure comprehensive monitoring

#### Regular Updates
- Update detection patterns monthly
- Review audit results weekly
- Update risk assessments quarterly
- Refresh configuration defaults

### 2. Operational Security

#### Session Management
- Enforce session caps strictly
- Implement mandatory breaks
- Vary session lengths
- Randomize login times

#### Behavior Patterns
- Maintain activity variance
- Implement idle behaviors
- Use social interactions
- Vary travel patterns

### 3. Monitoring & Response

#### Continuous Monitoring
- Monitor all detection surfaces
- Set up automated alerts
- Track performance metrics
- Maintain audit history

#### Incident Response
- Have emergency procedures ready
- Maintain backup configurations
- Document all incidents
- Learn from each event

## Troubleshooting

### 1. Common Issues

#### False Positives
**Problem**: System flags legitimate behavior as suspicious.

**Solution**:
```python
# Adjust sensitivity
def adjust_sensitivity(level):
    """Adjust detection sensitivity."""
    if level == "high":
        # Increase thresholds
        pass
    elif level == "low":
        # Decrease thresholds
        pass
```

#### Performance Impact
**Problem**: Safety features impact performance.

**Solution**:
```python
# Optimize performance
def optimize_performance():
    """Optimize safety feature performance."""
    # Reduce check frequency
    # Use efficient algorithms
    # Cache results
    pass
```

### 2. Configuration Issues

#### Configuration Conflicts
**Problem**: Multiple configurations conflict.

**Solution**:
```python
# Resolve conflicts
def resolve_config_conflicts():
    """Resolve configuration conflicts."""
    # Load all configurations
    # Identify conflicts
    # Apply resolution rules
    # Validate final configuration
    pass
```

#### Missing Dependencies
**Problem**: Required dependencies missing.

**Solution**:
```bash
# Install dependencies
pip install psutil
pip install requests
pip install discord.py
```

### 3. Integration Issues

#### System Integration
**Problem**: Safety features don't integrate with existing systems.

**Solution**:
```python
# Integration testing
def test_integration():
    """Test system integration."""
    # Test with identity_guard
    # Test with macro_watcher
    # Test with anti_detection
    # Validate all integrations
    pass
```

## Conclusion

This hardening guide provides comprehensive instructions for securing the MS11 system against detection. Key points:

1. **Enable all safety defaults** - This is critical for basic protection
2. **Implement humanization features** - These are essential for avoiding detection
3. **Monitor continuously** - Regular audits and monitoring are crucial
4. **Respond quickly** - Have emergency procedures ready
5. **Maintain vigilance** - Security is an ongoing process

Remember: The goal is to make the system appear as human-like as possible while maintaining functionality. Regular audits and updates are essential for maintaining security.

## Additional Resources

- [Detection Surface Checklist](safety/checklists/detection_surface.md)
- [Safety Defaults Configuration](config/safety_defaults.json)
- [Red-Team Audit Runner](safety/redteam/audit_runner.py)
- [Batch 170 Implementation Summary](BATCH_170_IMPLEMENTATION_SUMMARY.md)

For additional support or questions, refer to the project documentation or contact the development team. 