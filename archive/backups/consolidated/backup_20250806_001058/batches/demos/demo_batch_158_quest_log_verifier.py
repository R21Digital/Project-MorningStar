#!/usr/bin/env python3
"""
Demo script for Batch 158 - Quest Log Verifier (UI Scan Layer)

This demo showcases the visual OCR scanning of quest completion history
to verify quest progress using the quest log UI.
"""

import time
import random
from datetime import datetime
from typing import Dict, List, Optional

# Import the quest log UI scanner
try:
    from core.quest_log_ui_scanner import (
        QuestLogUIScanner,
        QuestLogScanResult,
        QuestChainScanResult,
        scan_quest_completion,
        scan_quest_chain_completion,
        should_skip_quest,
        should_skip_chain
    )
    SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Quest log UI scanner not available: {e}")
    SCANNER_AVAILABLE = False


class QuestLogVerifierDemo:
    """Demo class for Batch 158 - Quest Log Verifier (UI Scan Layer)."""
    
    def __init__(self):
        """Initialize the demo."""
        self.scanner = None
        self.demo_quests = [
            "Legacy Quest 1",
            "Heroic Quest 2", 
            "Epic Quest 3",
            "Daily Quest 1",
            "Weekly Quest 2"
        ]
        self.demo_chains = {
            "legacy": ["Legacy Quest 1", "Legacy Quest 2", "Legacy Quest 3"],
            "heroic": ["Heroic Quest 1", "Heroic Quest 2", "Heroic Quest 3"],
            "epic": ["Epic Quest 1", "Epic Quest 2", "Epic Quest 3"],
            "daily": ["Daily Quest 1", "Daily Quest 2"],
            "weekly": ["Weekly Quest 1", "Weekly Quest 2", "Weekly Quest 3"]
        }
        
    def setup_scanner(self) -> bool:
        """Set up the quest log UI scanner."""
        if not SCANNER_AVAILABLE:
            print("❌ Quest log UI scanner not available")
            return False
        
        try:
            # Initialize scanner with demo configuration
            config = {
                'quest_log_image_path': '/ui/questlog.png',
                'min_confidence': 70.0,
                'prompt_on_uncertain': True,
                'prompt_threshold': 50.0,
                'preprocessing_enabled': True,
                'contrast_enhancement': True,
                'noise_reduction': True
            }
            
            self.scanner = QuestLogUIScanner(config)
            print("✅ Quest log UI scanner initialized")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing scanner: {e}")
            return False
    
    def demo_quest_completion_scan(self, quest_name: str, chain_id: Optional[str] = None) -> None:
        """Demo scanning a single quest for completion status."""
        print(f"\n🔍 Scanning quest completion: {quest_name}")
        print("=" * 50)
        
        if not self.scanner:
            print("❌ Scanner not available")
            return
        
        try:
            # Simulate quest log image capture
            print("📸 Capturing quest log image...")
            time.sleep(0.5)
            
            # Perform the scan
            scan_result = self.scanner.scan_quest_completion(quest_name, chain_id)
            
            # Display results
            print(f"📊 Scan Results:")
            print(f"  Quest: {scan_result.quest_name}")
            print(f"  Completed: {'✅ Yes' if scan_result.is_completed else '❌ No'}")
            print(f"  Confidence: {scan_result.confidence:.1f}%")
            print(f"  Method: {scan_result.scan_method}")
            print(f"  UI Region: {scan_result.ui_region}")
            print(f"  OCR Text: {scan_result.ocr_text[:100]}...")
            print(f"  Matched Keywords: {scan_result.matched_keywords}")
            print(f"  Chain ID: {scan_result.chain_id or 'None'}")
            
            # Determine action
            if scan_result.is_completed and scan_result.confidence >= 70:
                print("🎯 Action: Skip quest (high confidence completed)")
            elif scan_result.confidence < 50:
                print("❓ Action: Prompt user for clarification")
            else:
                print("⏭️  Action: Continue with quest (not completed)")
                
        except Exception as e:
            print(f"❌ Error scanning quest: {e}")
    
    def demo_chain_completion_scan(self, chain_id: str) -> None:
        """Demo scanning an entire quest chain for completion status."""
        print(f"\n🔗 Scanning quest chain completion: {chain_id}")
        print("=" * 50)
        
        if not self.scanner:
            print("❌ Scanner not available")
            return
        
        try:
            # Get quest names for the chain
            quest_names = self.demo_chains.get(chain_id, [f"{chain_id} Quest 1"])
            
            # Simulate quest log image capture
            print("📸 Capturing quest log image...")
            time.sleep(0.5)
            
            # Perform the chain scan
            chain_result = self.scanner.scan_quest_chain_completion(chain_id, quest_names)
            
            # Display results
            print(f"📊 Chain Scan Results:")
            print(f"  Chain ID: {chain_result.chain_id}")
            print(f"  Total Quests: {chain_result.total_quests}")
            print(f"  Completed: {chain_result.completed_quests}")
            print(f"  Completion: {chain_result.completion_percentage:.1f}%")
            print(f"  Fully Completed: {'✅ Yes' if chain_result.is_fully_completed else '❌ No'}")
            print(f"  Pending Quests: {chain_result.pending_quests}")
            print(f"  Completed Quests: {chain_result.completed_quests_list}")
            print(f"  Scan Time: {chain_result.scan_time:.2f}s")
            print(f"  UI Regions Scanned: {len(chain_result.ui_regions_scanned)}")
            
            # Determine action
            if chain_result.is_fully_completed:
                print("🎯 Action: Skip entire chain (fully completed)")
            elif chain_result.completion_percentage > 80:
                print("❓ Action: Prompt user about high completion percentage")
            else:
                print("⏭️  Action: Continue with chain (not fully completed)")
                
        except Exception as e:
            print(f"❌ Error scanning chain: {e}")
    
    def demo_skip_logic(self, quest_name: str, chain_id: Optional[str] = None) -> None:
        """Demo the skip logic for quests and chains."""
        print(f"\n⏭️  Demo Skip Logic")
        print("=" * 50)
        
        if not self.scanner:
            print("❌ Scanner not available")
            return
        
        try:
            # Test quest skip logic
            print(f"🔍 Testing skip logic for quest: {quest_name}")
            should_skip = self.scanner.should_skip_quest(quest_name, chain_id, prompt_user=False)
            print(f"  Should Skip Quest: {'✅ Yes' if should_skip else '❌ No'}")
            
            # Test chain skip logic
            if chain_id:
                print(f"🔗 Testing skip logic for chain: {chain_id}")
                should_skip_chain = self.scanner.should_skip_chain(chain_id, prompt_user=False)
                print(f"  Should Skip Chain: {'✅ Yes' if should_skip_chain else '❌ No'}")
                
        except Exception as e:
            print(f"❌ Error in skip logic: {e}")
    
    def demo_user_prompts(self) -> None:
        """Demo user prompt functionality for uncertain results."""
        print(f"\n❓ Demo User Prompts")
        print("=" * 50)
        
        if not self.scanner:
            print("❌ Scanner not available")
            return
        
        try:
            # Simulate uncertain quest result
            print("🔍 Simulating uncertain quest result...")
            
            # Create a mock uncertain result
            uncertain_result = QuestLogScanResult(
                quest_name="Uncertain Quest",
                is_completed=False,
                confidence=45.0,  # Below threshold
                scan_method="OCR_Completed_Tab",
                timestamp=datetime.now(),
                ui_region=(100, 150, 800, 600),
                ocr_text="Some quest text with unclear completion status...",
                matched_keywords=["quest"],
                chain_id="demo"
            )
            
            print(f"📊 Uncertain Result:")
            print(f"  Quest: {uncertain_result.quest_name}")
            print(f"  Confidence: {uncertain_result.confidence:.1f}%")
            print(f"  OCR Text: {uncertain_result.ocr_text}")
            print(f"  Matched Keywords: {uncertain_result.matched_keywords}")
            
            print("\n💡 In a real scenario, this would prompt the user for clarification.")
            print("   The user can choose to skip the quest or continue with it.")
            
        except Exception as e:
            print(f"❌ Error in user prompts demo: {e}")
    
    def demo_ui_regions(self) -> None:
        """Demo the UI regions configuration."""
        print(f"\n🖥️  Demo UI Regions")
        print("=" * 50)
        
        if not self.scanner:
            print("❌ Scanner not available")
            return
        
        try:
            print("📋 Configured UI Regions:")
            for region_name, region in self.scanner.ui_regions.items():
                print(f"  {region.name}:")
                print(f"    Coordinates: {region.coordinates}")
                print(f"    Description: {region.description}")
                print(f"    Priority: {region.scan_priority}")
                print()
            
            print("🎯 Scan Priority:")
            print("  Higher priority regions are scanned first")
            print("  Early exit when high confidence is found")
            print("  Fallback to lower priority regions if needed")
            
        except Exception as e:
            print(f"❌ Error in UI regions demo: {e}")
    
    def demo_ocr_keywords(self) -> None:
        """Demo the OCR keywords and completion detection."""
        print(f"\n🔤 Demo OCR Keywords")
        print("=" * 50)
        
        if not self.scanner:
            print("❌ Scanner not available")
            return
        
        try:
            print("📝 Completion Keywords:")
            for keyword in self.scanner.completion_keywords[:10]:  # Show first 10
                print(f"  • {keyword}")
            print("  ... and more")
            
            print("\n🎯 Completion Symbols:")
            completion_symbols = ["✓", "☑", "✅", "DONE", "COMPLETE", "FINISHED"]
            for symbol in completion_symbols:
                print(f"  • {symbol}")
            
            print("\n💡 The scanner looks for these keywords and symbols")
            print("   in the OCR text to determine completion status.")
            
        except Exception as e:
            print(f"❌ Error in OCR keywords demo: {e}")
    
    def demo_image_processing(self) -> None:
        """Demo the image processing capabilities."""
        print(f"\n🖼️  Demo Image Processing")
        print("=" * 50)
        
        if not self.scanner:
            print("❌ Scanner not available")
            return
        
        try:
            print("🔧 Image Processing Features:")
            print(f"  Preprocessing Enabled: {'✅ Yes' if self.scanner.preprocessing_enabled else '❌ No'}")
            print(f"  Contrast Enhancement: {'✅ Yes' if self.scanner.contrast_enhancement else '❌ No'}")
            print(f"  Noise Reduction: {'✅ Yes' if self.scanner.noise_reduction else '❌ No'}")
            
            print("\n📊 Processing Steps:")
            print("  1. Convert to grayscale")
            print("  2. Enhance contrast (if enabled)")
            print("  3. Reduce noise (if enabled)")
            print("  4. Apply binary threshold")
            print("  5. Perform OCR on processed image")
            
        except Exception as e:
            print(f"❌ Error in image processing demo: {e}")
    
    def run_full_demo(self) -> None:
        """Run the complete demo."""
        print("🎯 BATCH 158 - QUEST LOG VERIFIER (UI SCAN LAYER) DEMO")
        print("=" * 60)
        print("Purpose: Visual OCR scanning of quest completion history")
        print("Features: Quest log UI scanning, completion detection, user prompts")
        print("=" * 60)
        
        # Setup scanner
        if not self.setup_scanner():
            return
        
        # Run individual demos
        self.demo_ui_regions()
        self.demo_ocr_keywords()
        self.demo_image_processing()
        
        # Demo quest completion scanning
        for quest_name in self.demo_quests[:3]:  # Demo first 3 quests
            self.demo_quest_completion_scan(quest_name)
            time.sleep(1)
        
        # Demo chain completion scanning
        for chain_id in list(self.demo_chains.keys())[:2]:  # Demo first 2 chains
            self.demo_chain_completion_scan(chain_id)
            time.sleep(1)
        
        # Demo skip logic
        self.demo_skip_logic("Demo Quest", "demo")
        
        # Demo user prompts
        self.demo_user_prompts()
        
        print("\n" + "=" * 60)
        print("✅ BATCH 158 DEMO COMPLETE")
        print("=" * 60)
        print("💡 Usage Examples:")
        print("  python src/main.py --mode quest --quest-log-verifier")
        print("  python src/main.py --mode quest --quest-log-verifier --prompt-user")
        print("  python src/main.py --mode quest --quest-log-verifier --chain-id legacy")


def main():
    """Main demo function."""
    demo = QuestLogVerifierDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main() 