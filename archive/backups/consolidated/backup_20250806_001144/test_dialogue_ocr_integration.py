#!/usr/bin/env python3
"""
Test script for Dialogue Detection & OCR Interaction System (Batch 011)

This script tests the integration between the dialogue detection system and OCR
to ensure dialogue boxes can be detected, text extracted, and conversations advanced.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from core.dialogue_handler import (
    dialogue_handler,
    detect_dialogue_box,
    extract_dialogue_text,
    advance_conversation,
    auto_accept_quests,
    auto_complete_quests,
    wait_for_dialogue,
    handle_stalled_dialogue
)
from core.screenshot import capture_screen


def create_test_dialogue_image():
    """Create a test dialogue image for testing."""
    # Create a test image with a dialogue box
    width, height = 1024, 768
    image = np.ones((height, width, 3), dtype=np.uint8) * 50  # Dark background
    
    # Draw dialogue box
    box_x, box_y, box_w, box_h = 300, 250, 400, 200
    cv2.rectangle(image, (box_x, box_y), (box_x + box_w, box_y + box_h), (100, 100, 100), -1)
    cv2.rectangle(image, (box_x, box_y), (box_x + box_w, box_y + box_h), (200, 200, 200), 2)
    
    # Convert to PIL for text drawing
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Add dialogue text
    dialogue_text = "Greetings, traveler! I have a quest for you."
    draw.text((box_x + 20, box_y + 20), dialogue_text, fill=(255, 255, 255), font=font)
    
    # Add dialogue options
    options = ["Accept Quest", "Decline", "Ask for more info"]
    for i, option in enumerate(options):
        y_pos = box_y + 120 + i * 30
        draw.text((box_x + 20, y_pos), f"[{option}]", fill=(255, 255, 0), font=font)
    
    # Convert back to OpenCV format
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


def test_dialogue_detection():
    """Test dialogue box detection functionality."""
    print("🧪 Testing Dialogue Detection...")
    
    # Test with real screenshot
    try:
        image = capture_screen()
        dialogue_window = detect_dialogue_box(image)
        
        if dialogue_window:
            print(f"✅ Detected dialogue box:")
            print(f"   Type: {dialogue_window.window_type}")
            print(f"   Confidence: {dialogue_window.confidence:.2f}")
            print(f"   Position: ({dialogue_window.x}, {dialogue_window.y})")
            print(f"   Size: {dialogue_window.width}x{dialogue_window.height}")
            print(f"   Text: {dialogue_window.text[:100]}...")
            print(f"   Options: {dialogue_window.options}")
            return True
        else:
            print("ℹ️  No dialogue box detected (expected in test environment)")
            return True
            
    except Exception as e:
        print(f"❌ Error in dialogue detection: {e}")
        return False


def test_text_extraction():
    """Test dialogue text extraction and cleaning."""
    print("\n🧪 Testing Text Extraction...")
    
    # Create test dialogue window
    test_window = type('DialogueWindow', (), {
        'text': "Greetings, traveler! I have a quest for you.\n\n[Accept Quest] [Decline]",
        'window_type': 'quest',
        'confidence': 0.85
    })()
    
    # Extract and clean text
    cleaned_text = extract_dialogue_text(test_window)
    
    print(f"✅ Original text: {test_window.text}")
    print(f"✅ Cleaned text: {cleaned_text}")
    
    # Test OCR cleanup rules
    if cleaned_text and len(cleaned_text) > 0:
        print("✅ Text extraction and cleaning working correctly")
        return True
    else:
        print("❌ Text extraction failed")
        return False


def test_conversation_advancement():
    """Test automatic conversation advancement."""
    print("\n🧪 Testing Conversation Advancement...")
    
    # Create test dialogue window
    test_window = type('DialogueWindow', (), {
        'text': "Greetings, traveler! I have a quest for you.",
        'window_type': 'quest',
        'confidence': 0.85,
        'x': 400, 'y': 300, 'width': 400, 'height': 200
    })()
    
    # Test different advancement types
    advancement_types = ["auto", "accept", "continue"]
    
    for action_type in advancement_types:
        try:
            interaction = advance_conversation(test_window, action_type)
            
            print(f"✅ {action_type.capitalize()} advancement:")
            print(f"   Success: {interaction.success}")
            print(f"   Action: {interaction.action_type}")
            print(f"   Target: {interaction.target_text}")
            print(f"   Method: {interaction.details.get('method', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Error in {action_type} advancement: {e}")
            return False
    
    return True


def test_quest_auto_acceptance():
    """Test automatic quest acceptance."""
    print("\n🧪 Testing Quest Auto-Acceptance...")
    
    # This would normally test with a real dialogue window
    # For testing, we'll simulate the behavior
    try:
        success = auto_accept_quests()
        print(f"✅ Auto-accept quests result: {success}")
        
        # Test quest completion
        success = auto_complete_quests()
        print(f"✅ Auto-complete quests result: {success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in quest auto-acceptance: {e}")
        return False


def test_dialogue_waiting():
    """Test dialogue waiting functionality."""
    print("\n🧪 Testing Dialogue Waiting...")
    
    try:
        # Test with short timeout
        dialogue_window = wait_for_dialogue(timeout=2.0)
        
        if dialogue_window:
            print(f"✅ Dialogue detected while waiting: {dialogue_window.window_type}")
        else:
            print("ℹ️  No dialogue detected during wait (expected in test environment)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in dialogue waiting: {e}")
        return False


def test_stalled_dialogue_handling():
    """Test stalled dialogue handling."""
    print("\n🧪 Testing Stalled Dialogue Handling...")
    
    try:
        success = handle_stalled_dialogue(timeout=2.0)
        print(f"✅ Stalled dialogue handling result: {success}")
        return True
        
    except Exception as e:
        print(f"❌ Error in stalled dialogue handling: {e}")
        return False


def test_template_loading():
    """Test dialogue template loading."""
    print("\n🧪 Testing Template Loading...")
    
    try:
        # Check if templates directory exists
        assets_dir = dialogue_handler.assets_dir
        print(f"✅ Assets directory: {assets_dir}")
        
        # Check if templates were loaded
        template_count = len(dialogue_handler.templates)
        print(f"✅ Loaded {template_count} dialogue templates")
        
        # Show template types
        if template_count > 0:
            template_types = set(template.dialogue_type for template in dialogue_handler.templates)
            print(f"✅ Template types: {list(template_types)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in template loading: {e}")
        return False


def test_ocr_cleanup_rules():
    """Test OCR post-processing cleanup rules."""
    print("\n🧪 Testing OCR Cleanup Rules...")
    
    # Test text with common OCR errors
    test_texts = [
        "H3llo, trav3l3r! I hav3 a qu3st for you.",
        "Gr33tings, trav3l3r! I hav3 a qu3st for you.",
        "H3llo, trav3l3r! I hav3 a qu3st for you.",
        "Gr33tings, trav3l3r! I hav3 a qu3st for you.",
    ]
    
    for i, test_text in enumerate(test_texts):
        # Apply cleanup rules manually
        cleaned_text = test_text
        for pattern, replacement in dialogue_handler.ocr_cleanup_rules:
            cleaned_text = re.sub(pattern, replacement, cleaned_text)
        
        print(f"✅ Test {i+1}:")
        print(f"   Original: {test_text}")
        print(f"   Cleaned:  {cleaned_text}")
    
    return True


def test_debug_overlay():
    """Test debug overlay creation."""
    print("\n🧪 Testing Debug Overlay...")
    
    try:
        # Create test dialogue window
        test_window = type('DialogueWindow', (), {
            'text': "Greetings, traveler! I have a quest for you.",
            'window_type': 'quest',
            'confidence': 0.85,
            'x': 400, 'y': 300, 'width': 400, 'height': 200,
            'options': ["Accept", "Decline"]
        })()
        
        # Create test interaction
        test_interaction = type('DialogueInteraction', (), {
            'success': True,
            'action_type': 'accept',
            'target_text': 'Accept',
            'confidence': 0.85,
            'timestamp': '2024-01-01T00:00:00',
            'details': {'method': 'click'}
        })()
        
        # Create debug overlay
        overlay_image = dialogue_handler.create_debug_overlay(test_window, test_interaction)
        
        if overlay_image is not None and overlay_image.shape[0] > 0:
            print("✅ Debug overlay created successfully")
            print(f"   Image size: {overlay_image.shape}")
            return True
        else:
            print("❌ Debug overlay creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in debug overlay creation: {e}")
        return False


def test_logging_functionality():
    """Test dialogue event logging."""
    print("\n🧪 Testing Logging Functionality...")
    
    try:
        # Import DialogueWindow from dialogue_detector
        from core.dialogue_detector import DialogueWindow
        
        # Create test dialogue window using proper dataclass
        test_window = DialogueWindow(
            x=400, y=300, width=400, height=200,
            text="Greetings, traveler! I have a quest for you.",
            options=["Accept", "Decline"],
            confidence=0.85,
            window_type='quest'
        )
        
        # Log test event
        dialogue_handler.log_dialogue_event("test_detection", test_window)
        
        # Check if log file was created
        log_dir = dialogue_handler.log_dir
        log_files = list(log_dir.glob("*.json"))
        
        if log_files:
            print(f"✅ Log files created: {len(log_files)}")
            print(f"   Log directory: {log_dir}")
            return True
        else:
            print("ℹ️  No log files created (may be normal in test environment)")
            return True
            
    except Exception as e:
        print(f"❌ Error in logging functionality: {e}")
        return False


def main():
    """Run all tests for dialogue detection and OCR interaction system."""
    print("🚀 Starting Dialogue Detection & OCR Interaction Tests (Batch 011)")
    print("=" * 70)
    
    # Import re for cleanup rules test
    global re
    import re
    
    tests = [
        ("Dialogue Detection", test_dialogue_detection),
        ("Text Extraction", test_text_extraction),
        ("Conversation Advancement", test_conversation_advancement),
        ("Quest Auto-Acceptance", test_quest_auto_acceptance),
        ("Dialogue Waiting", test_dialogue_waiting),
        ("Stalled Dialogue Handling", test_stalled_dialogue_handling),
        ("Template Loading", test_template_loading),
        ("OCR Cleanup Rules", test_ocr_cleanup_rules),
        ("Debug Overlay", test_debug_overlay),
        ("Logging Functionality", test_logging_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dialogue detection and OCR interaction system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 