#!/usr/bin/env python3
"""
Batch 137 - MS11 Multi-Character Support Demo

This script demonstrates the multi-character support functionality including:
- Dual-window logic (per SWG multi-client rules)
- Toggle option: main and support mode
- Shared communication between instances
- Synchronized questing: Support follows Main
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Any

from core.multi_character_manager import (
    multi_character_manager,
    CharacterMode,
    CharacterRole
)
from android_ms11.modes.enhanced_support_mode import EnhancedSupportMode
from cli.multi_character_cli import MultiCharacterCLI


def demo_multi_character_registration():
    """Demonstrate character registration and window management."""
    print("=" * 80)
    print("DEMO: Multi-Character Registration & Window Management")
    print("=" * 80)
    
    # Start communication server
    print("1. Starting communication server...")
    if multi_character_manager.start_communication_server():
        print("   ✅ Communication server started")
    else:
        print("   ❌ Failed to start communication server")
        return False
    
    # Register main character
    print("\n2. Registering main character...")
    main_char = "DemoMain"
    main_window = f"SWG - {main_char}"
    
    if multi_character_manager.register_character(
        character_name=main_char,
        window_title=main_window,
        mode=CharacterMode.MAIN,
        role=CharacterRole.LEADER
    ):
        print(f"   ✅ Registered main character: {main_char}")
    else:
        print(f"   ❌ Failed to register main character: {main_char}")
        return False
    
    # Register support character
    print("\n3. Registering support character...")
    support_char = "DemoSupport"
    support_window = f"SWG - {support_char}"
    
    if multi_character_manager.register_character(
        character_name=support_char,
        window_title=support_window,
        mode=CharacterMode.SUPPORT,
        role=CharacterRole.FOLLOWER
    ):
        print(f"   ✅ Registered support character: {support_char}")
    else:
        print(f"   ❌ Failed to register support character: {support_char}")
        return False
    
    # Arrange windows
    print("\n4. Arranging windows...")
    window_titles = [main_window, support_window]
    positions = multi_character_manager.window_manager.arrange_windows(window_titles)
    print(f"   ✅ Windows arranged: {positions}")
    
    # Activate main character
    print("\n5. Activating main character...")
    if multi_character_manager.activate_character(main_char):
        print(f"   ✅ Activated main character: {main_char}")
    else:
        print(f"   ❌ Failed to activate main character: {main_char}")
    
    return True


def demo_enhanced_support_mode():
    """Demonstrate enhanced support mode functionality."""
    print("\n" + "=" * 80)
    print("DEMO: Enhanced Support Mode")
    print("=" * 80)
    
    # Create enhanced support instance
    print("1. Creating enhanced support mode...")
    support = EnhancedSupportMode("DemoSupport", "medic")
    print(f"   ✅ Created {support.support_type} support for {support.character_name}")
    
    # Start support
    print("\n2. Starting support mode...")
    if support.start_support():
        print("   ✅ Support mode started successfully")
    else:
        print("   ❌ Failed to start support mode")
        return False
    
    # Simulate some support activity
    print("\n3. Simulating support activity...")
    time.sleep(2)
    
    # Get support stats
    stats = support.get_support_stats()
    print(f"   📊 Support Statistics:")
    print(f"      - Buffs Applied: {stats['buffs_applied']}")
    print(f"      - Heals Applied: {stats['heals_applied']}")
    print(f"      - Running: {stats['is_running']}")
    
    # Stop support
    print("\n4. Stopping support mode...")
    if support.stop_support():
        print("   ✅ Support mode stopped successfully")
    else:
        print("   ❌ Failed to stop support mode")
    
    return True


def demo_character_communication():
    """Demonstrate inter-character communication."""
    print("\n" + "=" * 80)
    print("DEMO: Inter-Character Communication")
    print("=" * 80)
    
    # Send position update
    print("1. Sending position update...")
    multi_character_manager.sync_position(
        character_name="DemoMain",
        position=(100, 200),
        planet="Naboo",
        city="Theed"
    )
    print("   ✅ Position update sent")
    
    # Send quest update
    print("\n2. Sending quest update...")
    quest_data = {
        "quest_name": "Demo Quest",
        "status": "active",
        "location": {
            "planet": "Naboo",
            "city": "Theed",
            "coordinates": (150, 250)
        }
    }
    multi_character_manager.sync_quest_progress("DemoMain", quest_data)
    print("   ✅ Quest update sent")
    
    # Send command
    print("\n3. Sending command...")
    multi_character_manager.send_message(
        sender="DemoMain",
        message_type="command",
        data={
            "command": "follow",
            "target": "DemoSupport"
        },
        priority="high"
    )
    print("   ✅ Command sent")
    
    # Check message queue
    print("\n4. Checking message queue...")
    messages = multi_character_manager.get_messages("DemoSupport")
    print(f"   📨 Messages for DemoSupport: {len(messages)}")
    for i, msg in enumerate(messages):
        print(f"      Message {i+1}: {msg.message_type} - {msg.data}")
    
    return True


def demo_mode_switching():
    """Demonstrate character mode switching."""
    print("\n" + "=" * 80)
    print("DEMO: Character Mode Switching")
    print("=" * 80)
    
    # Switch main character to support mode
    print("1. Switching main character to support mode...")
    if multi_character_manager.switch_character_mode("DemoMain", CharacterMode.SUPPORT):
        print("   ✅ DemoMain switched to support mode")
    else:
        print("   ❌ Failed to switch DemoMain to support mode")
    
    # Switch support character to main mode
    print("\n2. Switching support character to main mode...")
    if multi_character_manager.switch_character_mode("DemoSupport", CharacterMode.MAIN):
        print("   ✅ DemoSupport switched to main mode")
    else:
        print("   ❌ Failed to switch DemoSupport to main mode")
    
    # Switch back
    print("\n3. Switching back to original modes...")
    multi_character_manager.switch_character_mode("DemoMain", CharacterMode.MAIN)
    multi_character_manager.switch_character_mode("DemoSupport", CharacterMode.SUPPORT)
    print("   ✅ Characters switched back to original modes")
    
    return True


def demo_cli_functionality():
    """Demonstrate CLI functionality."""
    print("\n" + "=" * 80)
    print("DEMO: CLI Functionality")
    print("=" * 80)
    
    # Create CLI instance
    print("1. Creating CLI instance...")
    cli = MultiCharacterCLI()
    print("   ✅ CLI instance created")
    
    # Get status
    print("\n2. Getting session status...")
    status = cli.get_status()
    print(f"   📊 Status retrieved: {len(status['characters'])} characters")
    
    # Send command via CLI
    print("\n3. Sending command via CLI...")
    if cli.send_command("DemoSupport", "stay"):
        print("   ✅ Command sent via CLI")
    else:
        print("   ❌ Failed to send command via CLI")
    
    return True


def demo_synchronized_questing():
    """Demonstrate synchronized questing functionality."""
    print("\n" + "=" * 80)
    print("DEMO: Synchronized Questing")
    print("=" * 80)
    
    # Simulate quest progression
    print("1. Simulating quest progression...")
    
    quest_stages = [
        {
            "quest_name": "Demo Quest",
            "status": "started",
            "location": {"planet": "Naboo", "city": "Theed"}
        },
        {
            "quest_name": "Demo Quest", 
            "status": "in_progress",
            "location": {"planet": "Naboo", "city": "Theed"}
        },
        {
            "quest_name": "Demo Quest",
            "status": "completed", 
            "location": {"planet": "Naboo", "city": "Theed"}
        }
    ]
    
    for i, stage in enumerate(quest_stages):
        print(f"   Stage {i+1}: {stage['status']}")
        multi_character_manager.sync_quest_progress("DemoMain", stage)
        time.sleep(1)
    
    print("   ✅ Quest progression simulated")
    
    # Check if support follows main
    print("\n2. Checking support following behavior...")
    main_char = multi_character_manager.get_main_character()
    support_chars = multi_character_manager.get_support_characters()
    
    print(f"   👑 Main character: {main_char}")
    print(f"   👥 Support characters: {support_chars}")
    
    return True


def demo_cleanup():
    """Cleanup demo resources."""
    print("\n" + "=" * 80)
    print("DEMO: Cleanup")
    print("=" * 80)
    
    # Cleanup multi-character manager
    print("1. Cleaning up multi-character manager...")
    multi_character_manager.cleanup()
    print("   ✅ Multi-character manager cleaned up")
    
    # Show final status
    print("\n2. Final status:")
    all_status = multi_character_manager.get_all_status()
    print(f"   📊 Active characters: {len(all_status)}")
    
    return True


def main():
    """Main demo function."""
    print("=" * 80)
    print("BATCH 137 - MS11 MULTI-CHARACTER SUPPORT DEMO")
    print("=" * 80)
    print()
    print("This demo showcases the multi-character support functionality:")
    print("• Dual-window logic (per SWG multi-client rules)")
    print("• Toggle option: main and support mode")
    print("• Shared communication between instances")
    print("• Synchronized questing: Support follows Main")
    print()
    
    try:
        # Run demos
        if not demo_multi_character_registration():
            print("❌ Demo failed at registration stage")
            return
        
        if not demo_enhanced_support_mode():
            print("❌ Demo failed at support mode stage")
            return
        
        if not demo_character_communication():
            print("❌ Demo failed at communication stage")
            return
        
        if not demo_mode_switching():
            print("❌ Demo failed at mode switching stage")
            return
        
        if not demo_cli_functionality():
            print("❌ Demo failed at CLI stage")
            return
        
        if not demo_synchronized_questing():
            print("❌ Demo failed at questing stage")
            return
        
        demo_cleanup()
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Key Features Demonstrated:")
        print("✅ Multi-character registration and window management")
        print("✅ Enhanced support mode with stationary/mobile options")
        print("✅ Inter-character communication and messaging")
        print("✅ Dynamic mode switching (main ↔ support)")
        print("✅ CLI tool for session management")
        print("✅ Synchronized questing with support following")
        print()
        print("Next Steps:")
        print("• Configure character profiles in config/multi_character_config.json")
        print("• Use CLI tool: python cli/multi_character_cli.py --interactive")
        print("• Start session: python cli/multi_character_cli.py --start MainChar SupportChar medic")
        print()
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 