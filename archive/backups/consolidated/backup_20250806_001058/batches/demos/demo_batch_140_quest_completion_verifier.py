#!/usr/bin/env python3
"""
Batch 140 - Quest Completion Verifier Demo

This demo showcases the quest completion verification system that uses OCR to peek
at the quest log and verify if quests or chains are already completed before 
beginning automation.

Features:
- OCR-based quest log reading
- Memory-based quest completion checking
- Quest chain verification
- Configurable user prompts
- Caching for performance
- Integration with existing quest systems
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

# Import the quest completion verifier
from core.quest_completion_verifier import (
    QuestCompletionVerifier,
    QuestVerificationResult,
    QuestChainVerificationResult,
    get_quest_verifier,
    verify_quest_completion,
    verify_quest_chain_completion,
    should_skip_quest,
    should_skip_chain,
    get_next_pending_quest
)


class QuestCompletionVerifierDemo:
    """Demo class for showcasing quest completion verification functionality."""
    
    def __init__(self):
        """Initialize the demo with configuration."""
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize verifier with config
        self.verifier = QuestCompletionVerifier(self.config)
        
        # Demo quest data
        self.demo_quests = {
            'legacy': [
                'Legacy Quest 1: Introduction',
                'Legacy Quest 2: Training',
                'Legacy Quest 3: Final Test'
            ],
            'theme_park': [
                'Theme Park Intro: Welcome',
                'Theme Park Main: Adventure',
                'Theme Park Final: Victory'
            ],
            'heroic': [
                'Heroic Quest 1: Preparation',
                'Heroic Quest 2: Challenge',
                'Heroic Quest 3: Triumph'
            ],
            'daily': [
                'Daily Quest 1: Morning Tasks',
                'Daily Quest 2: Afternoon Duties'
            ],
            'weekly': [
                'Weekly Quest 1: Weekly Goals',
                'Weekly Quest 2: Weekly Challenges',
                'Weekly Quest 3: Weekly Rewards'
            ]
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/quest_verifier_demo.log')
            ]
        )
    
    def load_config(self) -> Dict:
        """Load configuration from file."""
        config_path = Path('config/quest_verifier_config.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            self.logger.warning("Config file not found, using default settings")
            return {}
    
    def demo_single_quest_verification(self):
        """Demo single quest completion verification."""
        print("\n" + "="*60)
        print("🔍 SINGLE QUEST VERIFICATION DEMO")
        print("="*60)
        
        test_quests = [
            "Legacy Quest 1: Introduction",
            "Theme Park Intro: Welcome", 
            "Heroic Quest 2: Challenge",
            "Daily Quest 1: Morning Tasks",
            "Weekly Quest 3: Weekly Rewards"
        ]
        
        for quest_name in test_quests:
            print(f"\n📋 Verifying quest: {quest_name}")
            
            # Verify quest completion
            result = self.verifier.verify_quest_completion(quest_name)
            
            # Display results
            status_emoji = "✅" if result.is_completed else "⏳"
            print(f"   {status_emoji} Status: {'Completed' if result.is_completed else 'Pending'}")
            print(f"   🎯 Confidence: {result.confidence:.1f}%")
            print(f"   🔧 Method: {result.method}")
            print(f"   ⏱️  Time: {result.verification_time:.3f}s")
            
            if result.matched_keywords:
                print(f"   🔑 Matched Keywords: {', '.join(result.matched_keywords)}")
            
            if result.quest_log_text:
                print(f"   📝 Quest Log Text: {result.quest_log_text[:100]}...")
    
    def demo_quest_chain_verification(self):
        """Demo quest chain completion verification."""
        print("\n" + "="*60)
        print("🔗 QUEST CHAIN VERIFICATION DEMO")
        print("="*60)
        
        for chain_id, quest_names in self.demo_quests.items():
            print(f"\n📚 Verifying chain: {chain_id.upper()}")
            
            # Verify chain completion
            result = self.verifier.verify_quest_chain_completion(chain_id, quest_names)
            
            # Display results
            chain_status = "✅ COMPLETED" if result.is_fully_completed else "⏳ IN PROGRESS"
            print(f"   {chain_status}")
            print(f"   📊 Progress: {result.completed_quests}/{result.total_quests} "
                  f"({result.completion_percentage:.1f}%)")
            print(f"   ⏱️  Time: {result.verification_time:.3f}s")
            
            if result.completed_quests_list:
                print(f"   ✅ Completed: {', '.join(result.completed_quests_list)}")
            
            if result.pending_quests:
                print(f"   ⏳ Pending: {', '.join(result.pending_quests)}")
    
    def demo_skip_logic(self):
        """Demo quest and chain skip logic."""
        print("\n" + "="*60)
        print("⏭️ SKIP LOGIC DEMO")
        print("="*60)
        
        # Test individual quest skip logic
        test_quest = "Legacy Quest 1: Introduction"
        print(f"\n🔍 Testing skip logic for quest: {test_quest}")
        
        should_skip = self.verifier.should_skip_quest(test_quest, prompt_user=False)
        print(f"   Should skip: {'Yes' if should_skip else 'No'}")
        
        # Test chain skip logic
        test_chain = "daily"
        print(f"\n🔍 Testing skip logic for chain: {test_chain}")
        
        should_skip_chain = self.verifier.should_skip_chain(test_chain, prompt_user=False)
        print(f"   Should skip chain: {'Yes' if should_skip_chain else 'No'}")
        
        # Test next pending quest
        next_quest = self.verifier.get_next_pending_quest(test_chain)
        if next_quest:
            print(f"   Next pending quest: {next_quest}")
        else:
            print(f"   No pending quests in chain")
    
    def demo_integration_with_quest_system(self):
        """Demo integration with existing quest system."""
        print("\n" + "="*60)
        print("🔧 INTEGRATION DEMO")
        print("="*60)
        
        # Simulate quest execution with verification
        quests_to_execute = [
            ("Legacy Quest 1: Introduction", "legacy"),
            ("Theme Park Intro: Welcome", "theme_park"),
            ("Heroic Quest 2: Challenge", "heroic"),
            ("Daily Quest 1: Morning Tasks", "daily")
        ]
        
        print("\n🎮 Simulating quest execution with verification:")
        
        for quest_name, chain_id in quests_to_execute:
            print(f"\n📋 Checking quest: {quest_name}")
            
            # Check if quest should be skipped
            if self.verifier.should_skip_quest(quest_name, chain_id, prompt_user=False):
                print(f"   ⏭️  SKIPPING - Quest already completed")
                continue
            
            # Simulate quest execution
            print(f"   🚀 EXECUTING - Starting quest automation")
            print(f"   📍 Chain: {chain_id}")
            
            # Simulate some execution time
            time.sleep(0.1)
            
            print(f"   ✅ COMPLETED - Quest execution finished")
    
    def demo_ocr_performance(self):
        """Demo OCR performance and accuracy."""
        print("\n" + "="*60)
        print("🔍 OCR PERFORMANCE DEMO")
        print("="*60)
        
        # Test different OCR methods
        test_quest = "Legacy Quest 1: Introduction"
        methods = ["standard", "aggressive", "conservative"]
        
        print(f"\n📊 Testing OCR methods for quest: {test_quest}")
        
        for method in methods:
            print(f"\n🔧 Method: {method.upper()}")
            
            # Simulate OCR verification with different methods
            start_time = time.time()
            
            # This would normally call the actual OCR engine
            # For demo purposes, we'll simulate results
            confidence = 75.0 + (hash(method) % 20)  # Simulate different confidence levels
            is_completed = hash(method) % 2 == 0  # Simulate completion status
            
            verification_time = time.time() - start_time
            
            print(f"   🎯 Confidence: {confidence:.1f}%")
            print(f"   ✅ Completed: {'Yes' if is_completed else 'No'}")
            print(f"   ⏱️  Time: {verification_time:.3f}s")
    
    def demo_caching_system(self):
        """Demo the caching system for performance."""
        print("\n" + "="*60)
        print("💾 CACHING SYSTEM DEMO")
        print("="*60)
        
        test_quest = "Legacy Quest 1: Introduction"
        
        print(f"\n🔄 Testing cache performance for quest: {test_quest}")
        
        # First verification (cache miss)
        print("\n📋 First verification (cache miss):")
        start_time = time.time()
        result1 = self.verifier.verify_quest_completion(test_quest)
        time1 = time.time() - start_time
        print(f"   ⏱️  Time: {time1:.3f}s")
        
        # Second verification (cache hit)
        print("\n📋 Second verification (cache hit):")
        start_time = time.time()
        result2 = self.verifier.verify_quest_completion(test_quest)
        time2 = time.time() - start_time
        print(f"   ⏱️  Time: {time2:.3f}s")
        
        # Performance comparison
        if time1 > 0:
            speedup = time1 / time2 if time2 > 0 else float('inf')
            print(f"   🚀 Speedup: {speedup:.1f}x faster with cache")
        
        # Clear cache
        print("\n🗑️  Clearing cache...")
        self.verifier.clear_cache()
        print("   ✅ Cache cleared")
    
    def demo_error_handling(self):
        """Demo error handling and fallback mechanisms."""
        print("\n" + "="*60)
        print("⚠️ ERROR HANDLING DEMO")
        print("="*60)
        
        # Test with invalid quest names
        invalid_quests = [
            "",
            "   ",
            "NonExistentQuest12345",
            "Quest With Special Characters: !@#$%^&*()"
        ]
        
        print("\n🔍 Testing error handling with invalid inputs:")
        
        for quest_name in invalid_quests:
            print(f"\n📋 Testing quest: '{quest_name}'")
            
            try:
                result = self.verifier.verify_quest_completion(quest_name)
                print(f"   ✅ Result: {'Completed' if result.is_completed else 'Pending'}")
                print(f"   🎯 Confidence: {result.confidence:.1f}%")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demo_configuration_options(self):
        """Demo configuration options and customization."""
        print("\n" + "="*60)
        print("⚙️ CONFIGURATION DEMO")
        print("="*60)
        
        print("\n📋 Current configuration:")
        print(f"   🎯 Min Confidence: {self.config.get('min_confidence', 70.0)}%")
        print(f"   🔄 Retry Attempts: {self.config.get('retry_attempts', 3)}")
        print(f"   ⏱️  Cache Duration: {self.config.get('cache_duration', 300)}s")
        print(f"   🔑 Completion Keywords: {len(self.config.get('completion_keywords', []))}")
        print(f"   📍 Quest Log Regions: {len(self.config.get('quest_log_regions', {}))}")
        
        # Show some configuration details
        completion_keywords = self.config.get('completion_keywords', [])
        if completion_keywords:
            print(f"\n🔑 Completion Keywords (first 5):")
            for keyword in completion_keywords[:5]:
                print(f"   - {keyword}")
            if len(completion_keywords) > 5:
                print(f"   ... and {len(completion_keywords) - 5} more")
    
    def run_comprehensive_demo(self):
        """Run the complete demo suite."""
        print("🚀 BATCH 140 - QUEST COMPLETION VERIFIER DEMO")
        print("="*60)
        print("This demo showcases the quest completion verification system")
        print("that uses OCR to peek at the quest log and verify completion")
        print("before beginning automation to reduce redundant questing.")
        print("="*60)
        
        try:
            # Run all demo sections
            self.demo_single_quest_verification()
            self.demo_quest_chain_verification()
            self.demo_skip_logic()
            self.demo_integration_with_quest_system()
            self.demo_ocr_performance()
            self.demo_caching_system()
            self.demo_error_handling()
            self.demo_configuration_options()
            
            print("\n" + "="*60)
            print("✅ DEMO COMPLETED SUCCESSFULLY")
            print("="*60)
            print("The quest completion verifier is ready for integration!")
            print("Key benefits:")
            print("  • Reduces redundant questing")
            print("  • Improves automation efficiency")
            print("  • Configurable user prompts")
            print("  • OCR and memory-based verification")
            print("  • Caching for performance")
            print("  • Error handling and fallbacks")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            self.logger.error(f"Demo failed: {e}", exc_info=True)


def main():
    """Main demo execution."""
    demo = QuestCompletionVerifierDemo()
    demo.run_comprehensive_demo()


if __name__ == "__main__":
    main() 