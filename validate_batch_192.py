#!/usr/bin/env python3
"""
Batch 192 - Discord Webhook Integration Validation
Quick validation script to check implementation status
"""

import os
import json

def check_implementation():
    print("🔍 Validating Batch 192 - Discord Webhook Integration")
    print("=" * 55)
    
    status = {"passed": 0, "failed": 0}
    
    # Check webhook implementation file
    if os.path.exists("api/hooks/discord-webhook.js"):
        print("✅ Discord webhook implementation exists")
        status["passed"] += 1
        
        with open("api/hooks/discord-webhook.js", 'r') as f:
            content = f.read()
            if 'sendModSubmission' in content and 'sendBugReport' in content:
                print("✅ Required webhook methods found")
                status["passed"] += 1
            else:
                print("❌ Required webhook methods missing")
                status["failed"] += 1
    else:
        print("❌ Discord webhook implementation missing")
        status["failed"] += 1
    
    # Check configuration file
    if os.path.exists("config/webhooks.json"):
        print("✅ Webhook configuration exists")
        status["passed"] += 1
        
        try:
            with open("config/webhooks.json", 'r') as f:
                config = json.load(f)
                if 'modSubmissions' in config.get('webhooks', {}) and 'bugReports' in config.get('webhooks', {}):
                    print("✅ Required webhook configurations found")
                    status["passed"] += 1
                else:
                    print("❌ Required webhook configurations missing")
                    status["failed"] += 1
        except Exception as e:
            print(f"❌ Configuration file invalid: {e}")
            status["failed"] += 1
    else:
        print("❌ Webhook configuration missing")
        status["failed"] += 1
    
    # Check bug submission integration
    if os.path.exists("api/submit_bug.js"):
        print("✅ Bug submission file exists")
        status["passed"] += 1
        
        with open("api/submit_bug.js", 'r') as f:
            content = f.read()
            if 'sendDiscordNotification' in content and 'discord-webhook.js' in content:
                print("✅ Bug submission Discord integration found")
                status["passed"] += 1
            else:
                print("❌ Bug submission Discord integration missing")
                status["failed"] += 1
    else:
        print("❌ Bug submission file missing")
        status["failed"] += 1
    
    # Check mod submission integration
    if os.path.exists("api/submit_mod.js"):
        print("✅ Mod submission file exists") 
        status["passed"] += 1
        
        with open("api/submit_mod.js", 'r') as f:
            content = f.read()
            if 'sendDiscordNotification' in content and 'discord-webhook.js' in content:
                print("✅ Mod submission Discord integration found")
                status["passed"] += 1
            else:
                print("❌ Mod submission Discord integration missing")
                status["failed"] += 1
    else:
        print("❌ Mod submission file missing")
        status["failed"] += 1
    
    print("\n" + "=" * 55)
    total = status["passed"] + status["failed"]
    success_rate = (status["passed"] / total * 100) if total > 0 else 0
    
    print(f"📊 Validation Results:")
    print(f"   Passed: {status['passed']}/{total}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if status["failed"] == 0:
        print("\n🎉 Implementation COMPLETE! All components validated.")
        print("\n💡 Next steps:")
        print("   1. Set DISCORD_MOD_WEBHOOK_URL environment variable")
        print("   2. Set DISCORD_BUG_WEBHOOK_URL environment variable") 
        print("   3. Test with sample submissions")
    else:
        print(f"\n⚠️  {status['failed']} validation(s) failed")
    
    return status["failed"] == 0

if __name__ == "__main__":
    success = check_implementation()
    exit(0 if success else 1)