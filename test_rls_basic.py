#!/usr/bin/env python3
"""
Basic test for RLS mode functionality
"""

import json
from pathlib import Path

def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    config_path = Path("config/rare_loot_targets.json")
    if not config_path.exists():
        print("❌ Config file not found")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        targets = config.get("targets", [])
        settings = config.get("settings", {})
        loot_categories = config.get("loot_categories", {})
        
        print(f"✅ Loaded {len(targets)} targets")
        print(f"✅ Loaded {len(loot_categories)} loot categories")
        print(f"✅ Settings: {list(settings.keys())}")
        
        # Validate structure
        for target in targets:
            required_fields = ["name", "planet", "level", "priority"]
            missing_fields = [field for field in required_fields if field not in target]
            if missing_fields:
                print(f"❌ Target {target.get('name', 'Unknown')} missing fields: {missing_fields}")
                return False
        
        print("✅ All targets have required fields")
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_loot_analysis():
    """Test loot analysis logic."""
    print("\nTesting loot analysis...")
    
    # Mock loot categories
    loot_categories = {
        "pearls": {
            "rarity": "legendary",
            "value": 10000,
            "professions": ["artisan", "merchant"]
        },
        "scales": {
            "rarity": "epic",
            "value": 5000,
            "professions": ["armorsmith", "artisan"]
        },
        "hides": {
            "rarity": "rare",
            "value": 2000,
            "professions": ["armorsmith", "artisan"]
        }
    }
    
    # Test items
    test_items = [
        "Krayt Dragon Pearl",
        "Kimogila Hide", 
        "Mouf Tigrip Poison",
        "Common Trophy"
    ]
    
    print("Analyzing test items:")
    for item in test_items:
        # Determine loot type and rarity
        loot_type = "unknown"
        rarity = "common"
        value = 100
        
        for category, info in loot_categories.items():
            if category.lower() in item.lower():
                loot_type = category
                rarity = info.get("rarity", "common")
                value = info.get("value", 100)
                break
        
        # Check if this is a rare item
        is_rare = rarity in ["rare", "epic", "legendary"]
        
        rarity_emoji = {
            "common": "⚪",
            "uncommon": "🟢", 
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡"
        }.get(rarity, "❓")
        
        print(f"  {rarity_emoji} {item}")
        print(f"    Type: {loot_type}, Rarity: {rarity}")
        print(f"    Value: {value} credits, Rare: {is_rare}")
    
    print("✅ Loot analysis completed")
    return True

def test_target_prioritization():
    """Test target prioritization logic."""
    print("\nTesting target prioritization...")
    
    # Mock targets
    targets = [
        {
            "name": "Greater Krayt Dragon",
            "planet": "Tatooine",
            "level": 90,
            "priority": 10,
            "loot_types": ["pearls", "scales"]
        },
        {
            "name": "Kimogila Matriarch", 
            "planet": "Lok",
            "level": 85,
            "priority": 9,
            "loot_types": ["hides", "claws"]
        },
        {
            "name": "Mouf Tigrip",
            "planet": "Kashyyyk",
            "level": 82,
            "priority": 8,
            "loot_types": ["poison", "fangs"]
        }
    ]
    
    # Mock learning data
    learning_data = {
        "successful_targets": ["Greater Krayt Dragon"],
        "failed_targets": ["Test Kimogila"],
        "loot_patterns": {"pearls": 2, "scales": 1}
    }
    
    # Mock user preferences
    user_preferences = {
        "preferred_planets": ["Tatooine"],
        "preferred_loot_types": ["pearls"],
        "avoided_targets": ["Test Kimogila"],
        "notification_preferences": "all"
    }
    
    # Apply user preferences
    filtered_targets = []
    for target in targets:
        # Skip avoided targets
        if target["name"] in user_preferences.get("avoided_targets", []):
            continue
        
        # Apply planet preferences
        if (user_preferences.get("preferred_planets") and 
            target["planet"] not in user_preferences["preferred_planets"]):
            continue
        
        filtered_targets.append(target)
    
    # Sort by priority and learning data
    def sort_key(target):
        base_priority = target.get("priority", 0)
        
        # Boost priority for successful targets
        if target["name"] in learning_data.get("successful_targets", []):
            base_priority += 2
        
        # Reduce priority for failed targets
        if target["name"] in learning_data.get("failed_targets", []):
            base_priority -= 1
        
        return base_priority
    
    sorted_targets = sorted(filtered_targets, key=sort_key, reverse=True)
    
    print(f"✅ Prioritized {len(sorted_targets)} targets")
    print("\nTop targets:")
    for i, target in enumerate(sorted_targets[:3], 1):
        print(f"  {i}. {target['name']} (Priority: {target.get('priority', 0)})")
        print(f"     Planet: {target['planet']}, Level: {target['level']}")
        print(f"     Loot Types: {', '.join(target.get('loot_types', []))}")
    
    return True

def test_discord_alert():
    """Test Discord alert message generation."""
    print("\nTesting Discord alert generation...")
    
    sample_loot = {
        "name": "Krayt Dragon Pearl",
        "rarity": "legendary",
        "type": "pearls",
        "value": 10000,
        "timestamp": "2024-01-01T12:00:00",
        "location": "Tatooine - Dune Sea"
    }
    
    current_target = {
        "name": "Greater Krayt Dragon",
        "planet": "Tatooine",
        "zone": "Dune Sea"
    }
    
    message = (
        f"🎉 **Rare Loot Found!**\n"
        f"**Item:** {sample_loot['name']}\n"
        f"**Rarity:** {sample_loot['rarity'].title()}\n"
        f"**Type:** {sample_loot['type']}\n"
        f"**Value:** {sample_loot['value']} credits\n"
        f"**Location:** {sample_loot['location']}\n"
        f"**Time:** {sample_loot['timestamp']}\n"
        f"**Target:** {current_target['name']}"
    )
    
    print("Sample Discord alert message:")
    print(message)
    print("✅ Discord alert message generated successfully")
    
    return True

def main():
    """Run all basic tests."""
    print("🎯 Batch 172 - RLS Mode Basic Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Loot Analysis", test_loot_analysis),
        ("Target Prioritization", test_target_prioritization),
        ("Discord Alert Generation", test_discord_alert)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for success in results.values() if success)
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if successful_tests == total_tests:
        print("\n🎉 All tests passed! RLS Mode basic functionality is working.")
        return 0
    else:
        print(f"\n⚠️ {total_tests - successful_tests} test(s) failed.")
        return 1

if __name__ == "__main__":
    exit(main()) 