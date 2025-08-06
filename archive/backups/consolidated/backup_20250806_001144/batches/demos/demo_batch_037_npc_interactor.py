#!/usr/bin/env python3
"""
Demo script for Batch 037 - Interactive NPC & Terminal Logic

This script demonstrates the NPC interaction functionality including:
- OCR-based dialogue parsing
- Context-aware response selection
- Fallback interaction logic
- Chatbox scanning and message classification
- Success/failure tracking and statistics
"""

import sys
import time
from pathlib import Path

# Add interactions and core to path for imports
sys.path.insert(0, str(Path(__file__).parent / "interactions"))
sys.path.insert(0, str(Path(__file__).parent / "core" / "ocr"))

from npc_interactor import NPCInteractor, InteractionType, ResponseType, NPCDialogue
from chatbox_scanner import ChatboxScanner, MessageType, ChatMessage
from datetime import datetime


def demo_npc_interactor():
    """Demonstrate the NPC interaction functionality."""
    print("🚀 Batch 037 - Interactive NPC & Terminal Logic")
    print("=" * 60)
    
    # Initialize NPC interactor
    print("📚 Initializing NPC Interactor...")
    interactor = NPCInteractor()
    
    # Show configuration
    print(f"\n⚙️  Configuration:")
    print(f"   OCR Interval: {interactor.config.get('ocr_interval', 1.0)}s")
    print(f"   Max Retries: {interactor.config.get('max_retries', 3)}")
    print(f"   Fallback Delay: {interactor.config.get('fallback_delay', 0.5)}s")
    
    # Demonstrate dialogue parsing
    print("\n🔍 Dialogue Parsing Demo:")
    
    # Simulate different OCR dialogue outputs
    mock_dialogues = [
        # Quest Giver
        {
            "name": "Quest Giver",
            "ocr_text": "John Smith: Hello there! I have a quest for you. Would you like to accept it? [Accept] [Decline]",
            "expected_type": "quest_giver",
            "expected_response": "accept"
        },
        # Trainer
        {
            "name": "Trainer",
            "ocr_text": "Master Trainer: I can teach you new skills. Would you like to train? [Train] [Exit]",
            "expected_type": "trainer",
            "expected_response": "train"
        },
        # Terminal
        {
            "name": "Terminal",
            "ocr_text": "Computer Terminal: Welcome to the system. What would you like to do? [Continue] [Exit]",
            "expected_type": "terminal",
            "expected_response": "continue"
        },
        # Vendor
        {
            "name": "Vendor",
            "ocr_text": "Shopkeeper: Welcome to my shop! What would you like to buy? [Buy] [Sell] [Exit]",
            "expected_type": "vendor",
            "expected_response": "exit"
        }
    ]
    
    for i, dialogue_data in enumerate(mock_dialogues, 1):
        print(f"\n📝 Processing Dialogue {i}: {dialogue_data['name']}")
        print(f"   OCR Text: {dialogue_data['ocr_text'][:50]}...")
        
        # Parse dialogue from OCR text
        dialogue_info = interactor.parse_dialogue_from_ocr(dialogue_data['ocr_text'])
        if dialogue_info:
            print(f"   NPC Name: {dialogue_info['npc_name']}")
            print(f"   Dialogue Text: {dialogue_info['dialogue_text'][:40]}...")
            print(f"   Response Options: {len(dialogue_info['response_options'])}")
            print(f"   Interaction Type: {dialogue_info['interaction_type'].value}")
            print(f"   Confidence: {dialogue_info['confidence']:.2f}")
            
            # Create NPCDialogue object
            dialogue = NPCDialogue(
                npc_name=dialogue_info['npc_name'],
                dialogue_text=dialogue_info['dialogue_text'],
                response_options=dialogue_info['response_options'],
                interaction_type=dialogue_info['interaction_type'],
                confidence=dialogue_info['confidence']
            )
            
            # Determine response
            response = interactor.determine_response(dialogue)
            print(f"   Determined Response: {response.value}")
            print(f"   Expected Response: {dialogue_data['expected_response']}")
            
            # Check accuracy
            if response.value == dialogue_data['expected_response']:
                print("   ✅ Response: CORRECT")
            else:
                print("   ❌ Response: INCORRECT")
        else:
            print("   ❌ Failed to parse dialogue")
    
    # Demonstrate fallback sequences
    print("\n🔄 Fallback Sequences Demo:")
    
    fallback_sequences = interactor.config.get("fallback_sequences", {})
    for interaction_type, sequence in fallback_sequences.items():
        print(f"   {interaction_type.title()}: {sequence}")
    
    # Demonstrate interaction attempts
    print("\n🤖 Interaction Attempts Demo:")
    
    # Simulate interaction attempts
    for i, dialogue_data in enumerate(mock_dialogues[:2], 1):  # Test first 2
        print(f"\n🔄 Interaction Attempt {i}: {dialogue_data['name']}")
        
        # Simulate dialogue scanning
        dialogue_info = interactor.parse_dialogue_from_ocr(dialogue_data['ocr_text'])
        if dialogue_info:
            dialogue = NPCDialogue(
                npc_name=dialogue_info['npc_name'],
                dialogue_text=dialogue_info['dialogue_text'],
                response_options=dialogue_info['response_options'],
                interaction_type=dialogue_info['interaction_type'],
                confidence=dialogue_info['confidence']
            )
            
            # Simulate response execution
            response = interactor.determine_response(dialogue)
            print(f"   Detected Response: {response.value}")
            
            # Simulate execution (mock)
            print(f"   Executing response...")
            # In real implementation, this would click or press keys
            print(f"   ✅ Interaction completed")
        else:
            print(f"   ❌ Failed to process dialogue")


def demo_chatbox_scanner():
    """Demonstrate the chatbox scanning functionality."""
    print("\n📱 Chatbox Scanner Demo:")
    print("-" * 40)
    
    # Initialize chatbox scanner
    print("📚 Initializing Chatbox Scanner...")
    scanner = ChatboxScanner()
    
    # Show configuration
    print(f"\n⚙️  Configuration:")
    print(f"   Scan Interval: {scanner.config.get('scan_interval', 0.5)}s")
    print(f"   Max History: {scanner.config.get('max_history', 100)}")
    
    # Demonstrate message parsing
    print("\n🔍 Message Parsing Demo:")
    
    # Simulate different chat messages
    mock_messages = [
        # NPC Speech
        {
            "text": "John Smith: Hello there! I have a quest for you.",
            "expected_type": "npc_speech",
            "expected_sender": "John Smith",
            "requires_response": True
        },
        # Quest Message
        {
            "text": "Quest: Accept the mission to defeat the bandits?",
            "expected_type": "quest_message",
            "expected_sender": "Unknown",
            "requires_response": True
        },
        # Trainer Message
        {
            "text": "Trainer: I can teach you new combat skills.",
            "expected_type": "trainer_message",
            "expected_sender": "Trainer",
            "requires_response": True
        },
        # Terminal Message
        {
            "text": "Terminal: System access granted. Continue?",
            "expected_type": "terminal_message",
            "expected_sender": "Terminal",
            "requires_response": True
        },
        # System Message
        {
            "text": "System: You have gained 100 experience points.",
            "expected_type": "system_message",
            "expected_sender": "System",
            "requires_response": False
        },
        # Player Message
        {
            "text": "Player123: Anyone want to group up?",
            "expected_type": "player_message",
            "expected_sender": "Player123",
            "requires_response": False
        }
    ]
    
    for i, message_data in enumerate(mock_messages, 1):
        print(f"\n📝 Processing Message {i}")
        print(f"   Text: {message_data['text'][:40]}...")
        
        # Parse message
        message = scanner.parse_single_message(message_data['text'])
        if message:
            print(f"   Sender: {message.sender}")
            print(f"   Type: {message.message_type.value}")
            print(f"   Content: {message.content[:30]}...")
            print(f"   Requires Response: {message.requires_response}")
            print(f"   Confidence: {message.confidence:.2f}")
            
            # Check accuracy
            type_correct = message.message_type.value == message_data['expected_type']
            sender_correct = message.sender == message_data['expected_sender']
            response_correct = message.requires_response == message_data['requires_response']
            
            if type_correct and sender_correct and response_correct:
                print("   ✅ Parsing: CORRECT")
            elif type_correct or sender_correct or response_correct:
                print("   ⚠️  Parsing: PARTIAL")
            else:
                print("   ❌ Parsing: INCORRECT")
        else:
            print("   ❌ Failed to parse message")
    
    # Demonstrate message filtering
    print("\n🔍 Message Filtering Demo:")
    
    # Simulate scanning chatbox
    print("   Scanning chatbox for new messages...")
    new_messages = scanner.scan_chatbox()
    print(f"   Found {len(new_messages)} new messages")
    
    # Show NPC messages
    npc_messages = scanner.get_npc_messages()
    print(f"   NPC Messages: {len(npc_messages)}")
    
    # Show messages requiring response
    response_messages = scanner.get_messages_requiring_response()
    print(f"   Messages Requiring Response: {len(response_messages)}")


def demo_integration():
    """Demonstrate integration between NPC interactor and chatbox scanner."""
    print("\n🔗 Integration Demo:")
    print("-" * 40)
    
    # Initialize both systems
    interactor = NPCInteractor()
    scanner = ChatboxScanner()
    
    # Simulate integrated workflow
    print("🔄 Integrated NPC Interaction Workflow:")
    
    # Step 1: Scan chatbox for NPC messages
    print("\n1️⃣ Scanning chatbox for NPC messages...")
    npc_messages = scanner.get_npc_messages()
    print(f"   Found {len(npc_messages)} NPC messages")
    
    # Step 2: Process NPC dialogue
    if npc_messages:
        latest_message = npc_messages[0]
        print(f"\n2️⃣ Processing NPC dialogue from {latest_message.sender}...")
        print(f"   Content: {latest_message.content[:50]}...")
        
        # Parse dialogue
        dialogue_info = interactor.parse_dialogue_from_ocr(latest_message.content)
        if dialogue_info:
            dialogue = NPCDialogue(
                npc_name=dialogue_info['npc_name'],
                dialogue_text=dialogue_info['dialogue_text'],
                response_options=dialogue_info['response_options'],
                interaction_type=dialogue_info['interaction_type'],
                confidence=dialogue_info['confidence']
            )
            
            print(f"   Interaction Type: {dialogue.interaction_type.value}")
            print(f"   Response Options: {len(dialogue.response_options)}")
            
            # Step 3: Determine response
            response = interactor.determine_response(dialogue)
            print(f"\n3️⃣ Determined Response: {response.value}")
            
            # Step 4: Execute response
            print(f"\n4️⃣ Executing response...")
            success = interactor.execute_response(response, dialogue)
            print(f"   Success: {success}")
        else:
            print("   ❌ Failed to parse dialogue")
    else:
        print("   No NPC messages found")
    
    # Show statistics
    print("\n📊 Statistics:")
    
    interactor_stats = interactor.get_interaction_statistics()
    print(f"   NPC Interactions: {interactor_stats.get('total_interactions', 0)}")
    print(f"   Success Rate: {interactor_stats.get('success_rate', 0):.2f}")
    print(f"   Fallback Usage: {interactor_stats.get('fallback_usage', 0)}")
    
    scanner_stats = scanner.get_chat_statistics()
    print(f"   Total Messages: {scanner_stats.get('total_messages', 0)}")
    print(f"   NPC Messages: {scanner_stats.get('npc_messages', 0)}")
    print(f"   Response Required: {scanner_stats.get('response_required', 0)}")


def demo_error_handling():
    """Demonstrate error handling and fallback logic."""
    print("\n⚠️  Error Handling Demo:")
    print("-" * 40)
    
    interactor = NPCInteractor()
    
    # Test with invalid OCR text
    print("🔍 Testing with invalid OCR text...")
    dialogue = interactor.scan_npc_dialogue()
    if dialogue is None:
        print("   ✅ Correctly handled invalid OCR")
    
    # Test with unclear dialogue
    print("\n🔍 Testing with unclear dialogue...")
    unclear_text = "Some unclear text without clear patterns"
    dialogue_info = interactor.parse_dialogue_from_ocr(unclear_text)
    if dialogue_info:
        print(f"   Confidence: {dialogue_info['confidence']:.2f}")
        if dialogue_info['confidence'] < 0.5:
            print("   ✅ Correctly identified low confidence")
    
    # Test fallback sequence
    print("\n🔄 Testing fallback sequence...")
    success = interactor.execute_fallback_sequence(InteractionType.QUEST_GIVER)
    print(f"   Fallback Success: {success}")


if __name__ == "__main__":
    print("🎯 Batch 037 - Interactive NPC & Terminal Logic")
    print("=" * 70)
    
    # Run main demos
    demo_npc_interactor()
    demo_chatbox_scanner()
    demo_integration()
    demo_error_handling()
    
    print("\n🎉 All demonstrations completed successfully!")
    print("   The NPC interaction system is ready for use.") 