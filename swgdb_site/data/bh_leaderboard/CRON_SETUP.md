# Bounty Hunter Leaderboard Cron Setup Guide

## Overview
This guide explains how to set up automated monthly season resets for the Bounty Hunter Leaderboard using cron jobs.

## Prerequisites
- Linux/Unix system with cron support
- Python 3.7+ installed
- Access to the SWGDB server

## Step 1: Verify Python Dependencies

### 1.1 Install Required Packages
```bash
pip install pyyaml
```

### 1.2 Test the Script
```bash
cd swgdb_site/data/bh_leaderboard
python cron_reset.py
```

Expected output:
```
ℹ️ No season reset needed
Current season: 9
Active hunters: 5
```

## Step 2: Set Up Cron Job

### 2.1 Edit Crontab
```bash
crontab -e
```

### 2.2 Add Cron Entry
Add one of the following entries depending on your preference:

#### Daily Check (Recommended)
```bash
# Check for season reset daily at 2 AM
0 2 * * * cd /path/to/swgdb_site/data/bh_leaderboard && python cron_reset.py >> leaderboard_cron.log 2>&1
```

#### Monthly Check (Alternative)
```bash
# Check for season reset on the 1st of each month at 2 AM
0 2 1 * * cd /path/to/swgdb_site/data/bh_leaderboard && python cron_reset.py >> leaderboard_cron.log 2>&1
```

#### Hourly Check (For Testing)
```bash
# Check for season reset every hour (for testing only)
0 * * * * cd /path/to/swgdb_site/data/bh_leaderboard && python cron_reset.py >> leaderboard_cron.log 2>&1
```

## Step 3: Verify Cron Job

### 3.1 Check Crontab
```bash
crontab -l
```

### 3.2 Test Manual Execution
```bash
cd /path/to/swgdb_site/data/bh_leaderboard
python cron_reset.py
```

### 3.3 Check Logs
```bash
tail -f leaderboard_cron.log
```

## Step 4: Discord Bot Integration

### 4.1 Install Discord.py
```bash
pip install discord.py
```

### 4.2 Configure Bot Token
Edit `discord_integration.py` and update:
```python
TOKEN = "your-actual-discord-bot-token"
CHANNEL_ID = 123456789  # Your actual channel ID
```

### 4.3 Run Discord Bot
```bash
python discord_integration.py
```

## Step 5: Monitoring and Maintenance

### 5.1 Log Monitoring
Check the cron logs regularly:
```bash
# View recent logs
tail -20 leaderboard_cron.log

# Search for errors
grep "ERROR" leaderboard_cron.log

# Search for successful resets
grep "Season reset performed" leaderboard_cron.log
```

### 5.2 File Permissions
Ensure proper permissions:
```bash
chmod +x cron_reset.py
chmod +x leaderboard_manager.py
chmod 644 *.yml
```

### 5.3 Backup Strategy
Set up regular backups of the leaderboard data:
```bash
# Add to crontab for daily backups
0 1 * * * tar -czf /backup/bh_leaderboard_$(date +\%Y\%m\%d).tar.gz /path/to/swgdb_site/data/bh_leaderboard/
```

## Step 6: Troubleshooting

### 6.1 Common Issues

#### Cron Job Not Running
```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
sudo tail -f /var/log/cron
```

#### Python Path Issues
```bash
# Use full path to Python
which python3
# Update cron entry with full path
0 2 * * * /usr/bin/python3 /path/to/swgdb_site/data/bh_leaderboard/cron_reset.py
```

#### Permission Issues
```bash
# Check file permissions
ls -la /path/to/swgdb_site/data/bh_leaderboard/

# Fix permissions if needed
chmod 755 /path/to/swgdb_site/data/bh_leaderboard/
chmod 644 /path/to/swgdb_site/data/bh_leaderboard/*.yml
```

### 6.2 Debug Mode
For testing, you can run the script in debug mode:
```bash
python cron_reset.py --debug
```

## Step 7: Advanced Configuration

### 7.1 Custom Season Length
Edit `current_season.yml` to change season duration:
```yaml
settings:
  auto_reset: true
  reset_day: 1
  reset_month: true  # Set to false for custom intervals
```

### 7.2 Multiple Cron Jobs
For more complex setups, you can add multiple cron jobs:
```bash
# Daily check for resets
0 2 * * * cd /path/to/swgdb_site/data/bh_leaderboard && python cron_reset.py

# Weekly backup
0 3 * * 0 tar -czf /backup/bh_leaderboard_weekly_$(date +\%Y\%m\%d).tar.gz /path/to/swgdb_site/data/bh_leaderboard/

# Monthly cleanup of old logs
0 4 1 * * find /path/to/swgdb_site/data/bh_leaderboard/ -name "*.log" -mtime +30 -delete
```

### 7.3 Email Notifications
Add email notifications for season resets:
```bash
# Add to cron entry
0 2 * * * cd /path/to/swgdb_site/data/bh_leaderboard && python cron_reset.py && echo "Season reset check completed" | mail -s "BH Leaderboard Update" admin@swgdb.com
```

## Step 8: Security Considerations

### 8.1 File Permissions
```bash
# Restrict access to leaderboard files
chmod 600 /path/to/swgdb_site/data/bh_leaderboard/*.yml
chown www-data:www-data /path/to/swgdb_site/data/bh_leaderboard/
```

### 8.2 Log Rotation
Set up log rotation to prevent disk space issues:
```bash
# Add to /etc/logrotate.d/bh_leaderboard
/path/to/swgdb_site/data/bh_leaderboard/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## Step 9: Performance Optimization

### 9.1 Database Integration
For high-traffic sites, consider moving to a database:
```python
# Example: SQLite integration
import sqlite3

def add_kill_db(hunter_name, guild, bounty):
    conn = sqlite3.connect('bh_leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO kills (hunter_name, guild, bounty, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    ''', (hunter_name, guild, bounty))
    conn.commit()
    conn.close()
```

### 9.2 Caching
Implement caching for frequently accessed data:
```python
import functools
import time

@functools.lru_cache(maxsize=128)
def get_current_leaderboard():
    # Cache leaderboard data for 5 minutes
    return load_current_season()
```

## Step 10: Monitoring Dashboard

### 10.1 Health Check Script
Create a health check script:
```bash
#!/bin/bash
# health_check.sh

LOG_FILE="/path/to/swgdb_site/data/bh_leaderboard/leaderboard_cron.log"
LAST_LOG=$(tail -1 "$LOG_FILE" 2>/dev/null)

if [[ $LAST_LOG == *"ERROR"* ]]; then
    echo "CRITICAL: BH Leaderboard cron job has errors"
    exit 1
elif [[ $LAST_LOG == *"Season reset performed"* ]]; then
    echo "OK: Season reset completed successfully"
    exit 0
else
    echo "WARNING: No recent activity in leaderboard logs"
    exit 2
fi
```

### 10.2 Add to Monitoring
```bash
# Add to your monitoring system (e.g., Nagios)
/usr/local/bin/health_check.sh
```

## Support

For issues or questions:
- Check the logs: `tail -f leaderboard_cron.log`
- Test manually: `python cron_reset.py`
- Review configuration: `cat current_season.yml`

## Files Overview

- `cron_reset.py` - Main cron job script
- `leaderboard_manager.py` - Core leaderboard logic
- `current_season.yml` - Current season data
- `seasons/` - Archived season files
- `discord_integration.py` - Discord bot integration
- `leaderboard_cron.log` - Cron job logs 