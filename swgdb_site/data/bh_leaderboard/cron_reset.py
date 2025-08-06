#!/usr/bin/env python3
"""
Cron job script for automated BH leaderboard season resets
Run this script daily to check for season resets
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the manager
sys.path.append(str(Path(__file__).parent))

from leaderboard_manager import BHLeaderboardManager

def main():
    """Main cron job function"""
    try:
        # Initialize the manager
        manager = BHLeaderboardManager()
        
        # Check for season reset
        if manager.check_season_reset():
            print("✅ Season reset performed successfully")
            return 0
        else:
            print("ℹ️ No season reset needed")
            return 0
            
    except Exception as e:
        print(f"❌ Error in cron job: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 