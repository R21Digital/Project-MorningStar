#!/usr/bin/env python3
"""Demo script for Batch 047 - Smart Quest Detection: NPC + Signal Scanner."""

import json
import logging
import time
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import our modules
from core.quest_scanner import SmartQuestScanner, QuestDetection, QuestDetectionMethod
from utils.npc_signal_detector import NPCSignalDetector, NPCDetectionResult, SignalType


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('demo_batch_047.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def create_mock_screen_with_npcs() -> np.ndarray:
    """Create a mock screen with NPCs and quest signals for testing."""
    # Create a mock screen (1200x800)
    screen = np.zeros((800, 1200, 3), dtype=np.uint8)
    
    # Add some background color
    screen[:] = (50, 50, 50)  # Dark gray background
    
    # Add mock NPCs with quest signals
    npc_positions = [
        ((300, 200), "Yevin Rook", (255, 255, 0)),      # Yellow quest icon
        ((600, 300), "Captain Gavyn Sykes", (255, 165, 0)),  # Orange quest icon
        ((900, 400), "Mara Jade", (255, 0, 0)),         # Red quest icon
        ((150, 500), "Jar Jar Binks", (0, 0, 255)),     # Blue quest icon
    ]
    
    for (x, y), npc_name, color in npc_positions:
        # Draw NPC (simple circle)
        cv2.circle(screen, (x, y), 30, (255, 255, 255), -1)
        
        # Draw quest icon above NPC
        cv2.circle(screen, (x, y - 50), 15, color, -1)
        
        # Add NPC name text (simulated)
        cv2.putText(screen, npc_name, (x - 50, y + 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return screen


def test_quest_scanner():
    """Test the smart quest scanner."""
    logger = setup_logging()
    logger.info("Starting Batch 047 Smart Quest Detection Demo")
    
    # Initialize scanner
    scanner = SmartQuestScanner()
    logger.info("Smart Quest Scanner initialized")
    
    # Add some test quest givers
    test_quest_givers = [
        {
            "planet": "naboo",
            "npc_name": "Yevin Rook",
            "quest_info": {
                "quest_id": "naboo_001",
                "quest_line": "Naboo Introduction",
                "quest_type": "delivery",
                "level_requirement": 1,
                "is_tracked": False
            }
        },
        {
            "planet": "naboo",
            "npc_name": "Captain Gavyn Sykes",
            "quest_info": {
                "quest_id": "naboo_002",
                "quest_line": "Naboo Security",
                "quest_type": "combat",
                "level_requirement": 5,
                "is_tracked": False
            }
        },
        {
            "planet": "naboo",
            "npc_name": "Mara Jade",
            "quest_info": {
                "quest_id": "naboo_003",
                "quest_line": "Naboo Diplomacy",
                "quest_type": "diplomatic",
                "level_requirement": 10,
                "is_tracked": False
            }
        }
    ]
    
    # Add quest givers to scanner
    for quest_giver in test_quest_givers:
        scanner.add_quest_giver(
            quest_giver["planet"],
            quest_giver["npc_name"],
            quest_giver["quest_info"]
        )
        logger.info(f"Added quest giver: {quest_giver['npc_name']}")
    
    # Create mock screen
    mock_screen = create_mock_screen_with_npcs()
    logger.info("Created mock screen with NPCs and quest signals")
    
    # Test quest scanning
    logger.info("Testing quest scanning...")
    detections = scanner.scan_for_quests("naboo", (600, 400))
    
    logger.info(f"Found {len(detections)} quest detections")
    for detection in detections:
        logger.info(f"  - NPC: {detection.npc_name}")
        logger.info(f"    Quest ID: {detection.quest_id}")
        logger.info(f"    Quest Line: {detection.quest_line}")
        logger.info(f"    Detection Method: {detection.detection_method.value}")
        logger.info(f"    Confidence: {detection.confidence:.2f}")
        logger.info(f"    Signals: {len(detection.signals)}")
        logger.info(f"    Is New Quest: {detection.is_new_quest}")
        logger.info("")
    
    # Get detection summary
    summary = scanner.get_detection_summary()
    logger.info(f"Detection Summary: {summary}")
    
    return scanner, detections


def test_npc_signal_detector():
    """Test the NPC signal detector."""
    logger = setup_logging()
    logger.info("Testing NPC Signal Detector")
    
    # Initialize detector
    detector = NPCSignalDetector()
    logger.info("NPC Signal Detector initialized")
    
    # Create mock screen
    mock_screen = create_mock_screen_with_npcs()
    logger.info("Created mock screen for testing")
    
    # Test NPC and signal detection
    logger.info("Testing NPC and signal detection...")
    npc_results = detector.detect_npcs_and_signals(mock_screen)
    
    logger.info(f"Found {len(npc_results)} NPC detections")
    for result in npc_results:
        logger.info(f"  - NPC: {result.npc_name}")
        logger.info(f"    Location: {result.location}")
        logger.info(f"    Confidence: {result.confidence:.2f}")
        logger.info(f"    Has Quest Signal: {result.has_quest_signal}")
        logger.info(f"    Signals: {len(result.signals)}")
        
        for signal in result.signals:
            logger.info(f"      Signal: {signal.signal_type.value}")
            logger.info(f"        Confidence: {signal.confidence:.2f}")
            logger.info(f"        Location: {signal.location}")
            logger.info(f"        Visual Indicators: {signal.visual_indicators}")
        logger.info("")
    
    # Get detection summary
    summary = detector.get_detection_summary()
    logger.info(f"NPC Detection Summary: {summary}")
    
    return detector, npc_results


def test_quest_database_integration():
    """Test quest database integration."""
    logger = setup_logging()
    logger.info("Testing Quest Database Integration")
    
    # Initialize scanner
    scanner = SmartQuestScanner()
    
    # Test quest database loading
    logger.info("Testing quest database loading...")
    quest_db = scanner._load_quest_database()
    logger.info(f"Loaded quest database with {len(quest_db)} planets")
    
    for planet, quests in quest_db.items():
        logger.info(f"  Planet: {planet} - {len(quests)} quests")
    
    # Test planet quest givers loading
    logger.info("Testing planet quest givers loading...")
    quest_givers = scanner._load_planet_quest_givers()
    logger.info(f"Loaded quest givers for {len(quest_givers)} planets")
    
    for planet, data in quest_givers.items():
        givers = data.get('quest_givers', [])
        logger.info(f"  Planet: {planet} - {len(givers)} quest givers")
    
    return scanner


def test_whisper_notification():
    """Test whisper notification for new quests."""
    logger = setup_logging()
    logger.info("Testing Whisper Notification System")
    
    # Initialize scanner
    scanner = SmartQuestScanner()
    
    # Add a new untracked quest
    scanner.add_quest_giver("naboo", "New Quest NPC", {
        "quest_id": "naboo_new_001",
        "quest_line": "New Quest Line",
        "quest_type": "exploration",
        "level_requirement": 3,
        "is_tracked": False
    })
    
    # Simulate detection of new quest
    mock_detection = QuestDetection(
        quest_id="naboo_new_001",
        npc_name="New Quest NPC",
        planet="naboo",
        location=(500, 300),
        detection_method=QuestDetectionMethod.COMBINED_SIGNAL,
        confidence=0.85,
        detected_at=datetime.now(),
        is_new_quest=True,
        is_tracked=False
    )
    
    # Test notification
    logger.info("Simulating new quest detection...")
    scanner._notify_new_quests([mock_detection])
    
    logger.info("Whisper notification test completed")
    
    return scanner


def run_comprehensive_test():
    """Run comprehensive test of all Batch 047 features."""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("BATCH 047 - SMART QUEST DETECTION COMPREHENSIVE TEST")
    logger.info("=" * 60)
    
    try:
        # Test 1: Quest Scanner
        logger.info("\n1. Testing Smart Quest Scanner...")
        scanner, detections = test_quest_scanner()
        
        # Test 2: NPC Signal Detector
        logger.info("\n2. Testing NPC Signal Detector...")
        detector, npc_results = test_npc_signal_detector()
        
        # Test 3: Quest Database Integration
        logger.info("\n3. Testing Quest Database Integration...")
        test_quest_database_integration()
        
        # Test 4: Whisper Notification
        logger.info("\n4. Testing Whisper Notification...")
        test_whisper_notification()
        
        # Test 5: Integration Test
        logger.info("\n5. Testing Integration...")
        test_integration(scanner, detector)
        
        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise


def test_integration(scanner: SmartQuestScanner, detector: NPCSignalDetector):
    """Test integration between scanner and detector."""
    logger = setup_logging()
    logger.info("Testing Scanner-Detector Integration")
    
    # Create mock screen
    mock_screen = create_mock_screen_with_npcs()
    
    # Use detector to find NPCs and signals
    npc_results = detector.detect_npcs_and_signals(mock_screen)
    
    # Use scanner to process detections
    detections = scanner.scan_for_quests("naboo", (600, 400))
    
    logger.info(f"Integration test results:")
    logger.info(f"  - NPC Detector found: {len(npc_results)} NPCs")
    logger.info(f"  - Quest Scanner found: {len(detections)} quests")
    
    # Check for matches
    npc_names = [result.npc_name for result in npc_results]
    quest_npcs = [detection.npc_name for detection in detections]
    
    matches = set(npc_names) & set(quest_npcs)
    logger.info(f"  - Matched NPCs: {len(matches)}")
    for match in matches:
        logger.info(f"    - {match}")
    
    return len(matches) > 0


def main():
    """Main demo function."""
    print("Batch 047 - Smart Quest Detection Demo")
    print("=" * 50)
    
    try:
        run_comprehensive_test()
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main() 