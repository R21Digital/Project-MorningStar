#!/usr/bin/env python3
"""
CLI interface for Batch 037 - Interactive NPC & Terminal Logic

Provides commands for:
- Testing NPC interactions
- Scanning chatbox messages
- Viewing interaction statistics
- Managing fallback sequences
- Testing OCR parsing
"""

import sys
import argparse
import time
from pathlib import Path

# Add interactions and core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "interactions"))
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "ocr"))

from npc_interactor import NPCInteractor, InteractionType, ResponseType, NPCDialogue
from chatbox_scanner import ChatboxScanner, MessageType, ChatMessage


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="NPC Interaction System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ms11 npc-interactor --test-dialogue "John: Hello there! [Accept] [Decline]"
  ms11 npc-interactor --interact-with-npc "John Smith"
  ms11 npc-interactor --scan-chatbox
  ms11 npc-interactor --show-stats
  ms11 npc-interactor --test-ocr "Quest: Accept the mission?"
        """
    )
    
    # Main commands
    parser.add_argument("--test-dialogue", type=str, metavar="TEXT",
                       help="Test dialogue parsing with OCR text")
    parser.add_argument("--interact-with-npc", type=str, metavar="NPC_NAME",
                       help="Interact with a specific NPC")
    parser.add_argument("--scan-chatbox", action="store_true",
                       help="Scan chatbox for new messages")
    parser.add_argument("--show-stats", action="store_true",
                       help="Show interaction and chat statistics")
    parser.add_argument("--test-ocr", type=str, metavar="TEXT",
                       help="Test OCR parsing with sample text")
    parser.add_argument("--list-fallbacks", action="store_true",
                       help="List all fallback sequences")
    parser.add_argument("--test-fallback", type=str, metavar="TYPE",
                       choices=["quest_giver", "trainer", "terminal", "vendor"],
                       help="Test fallback sequence for interaction type")
    parser.add_argument("--clear-history", action="store_true",
                       help="Clear interaction and chat history")
    parser.add_argument("--config", type=str, metavar="PATH",
                       help="Path to configuration file")
    
    # Optional arguments
    parser.add_argument("--max-retries", type=int, default=3,
                       help="Maximum retries for NPC interaction (default: 3)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize systems
    interactor = NPCInteractor(args.config)
    scanner = ChatboxScanner(args.config)
    
    if args.verbose:
        print("🔧 Initializing NPC Interaction System...")
        print(f"   Config: {args.config or 'default'}")
        print(f"   Max Retries: {args.max_retries}")
    
    # Execute commands
    if args.test_dialogue:
        test_dialogue_parsing(interactor, args.test_dialogue, args.verbose)
    
    elif args.interact_with_npc:
        interact_with_npc(interactor, args.interact_with_npc, args.max_retries, args.verbose)
    
    elif args.scan_chatbox:
        scan_chatbox(scanner, args.verbose)
    
    elif args.show_stats:
        show_statistics(interactor, scanner, args.verbose)
    
    elif args.test_ocr:
        test_ocr_parsing(scanner, args.test_ocr, args.verbose)
    
    elif args.list_fallbacks:
        list_fallback_sequences(interactor, args.verbose)
    
    elif args.test_fallback:
        test_fallback_sequence(interactor, args.test_fallback, args.verbose)
    
    elif args.clear_history:
        clear_history(interactor, scanner, args.verbose)
    
    else:
        # Default: show help
        parser.print_help()


def test_dialogue_parsing(interactor: NPCInteractor, ocr_text: str, verbose: bool):
    """Test dialogue parsing with OCR text."""
    print("🔍 Testing Dialogue Parsing")
    print("-" * 40)
    print(f"OCR Text: {ocr_text}")
    
    # Parse dialogue
    dialogue_info = interactor.parse_dialogue_from_ocr(ocr_text)
    if dialogue_info:
        print(f"\n✅ Parsing Results:")
        print(f"   NPC Name: {dialogue_info['npc_name']}")
        print(f"   Dialogue Text: {dialogue_info['dialogue_text']}")
        print(f"   Response Options: {dialogue_info['response_options']}")
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
        
        if verbose:
            print(f"\n📋 Detailed Analysis:")
            print(f"   Text Length: {len(ocr_text)} characters")
            print(f"   Response Options Count: {len(dialogue_info['response_options'])}")
            print(f"   Interaction Type Confidence: {dialogue_info['confidence']:.2f}")
    else:
        print("❌ Failed to parse dialogue")


def interact_with_npc(interactor: NPCInteractor, npc_name: str, max_retries: int, verbose: bool):
    """Interact with a specific NPC."""
    print(f"🤖 Interacting with NPC: {npc_name}")
    print("-" * 40)
    
    if verbose:
        print(f"   Max Retries: {max_retries}")
        print(f"   Starting interaction...")
    
    # Attempt interaction
    start_time = time.time()
    success = interactor.interact_with_npc(npc_name, max_retries)
    end_time = time.time()
    
    if success:
        print("✅ NPC interaction successful")
    else:
        print("❌ NPC interaction failed")
    
    if verbose:
        print(f"   Duration: {end_time - start_time:.2f} seconds")
        print(f"   Retries used: {max_retries}")


def scan_chatbox(scanner: ChatboxScanner, verbose: bool):
    """Scan chatbox for new messages."""
    print("📱 Scanning Chatbox")
    print("-" * 40)
    
    # Scan for new messages
    new_messages = scanner.scan_chatbox()
    print(f"Found {len(new_messages)} new messages")
    
    if new_messages:
        print("\n📝 New Messages:")
        for i, message in enumerate(new_messages, 1):
            print(f"   {i}. {message.sender}: {message.content[:50]}...")
            print(f"      Type: {message.message_type.value}")
            print(f"      Requires Response: {message.requires_response}")
            print(f"      Confidence: {message.confidence:.2f}")
    
    # Show recent NPC messages
    npc_messages = scanner.get_npc_messages()
    print(f"\n👥 Recent NPC Messages: {len(npc_messages)}")
    
    # Show messages requiring response
    response_messages = scanner.get_messages_requiring_response()
    print(f"❓ Messages Requiring Response: {len(response_messages)}")
    
    if verbose and response_messages:
        print("\n⚠️  Messages Requiring Response:")
        for message in response_messages:
            print(f"   {message.sender}: {message.content[:40]}...")


def show_statistics(interactor: NPCInteractor, scanner: ChatboxScanner, verbose: bool):
    """Show interaction and chat statistics."""
    print("📊 System Statistics")
    print("-" * 40)
    
    # NPC Interaction Statistics
    interactor_stats = interactor.get_interaction_statistics()
    print("\n🤖 NPC Interaction Statistics:")
    print(f"   Total Interactions: {interactor_stats.get('total_interactions', 0)}")
    print(f"   Successful Interactions: {interactor_stats.get('successful_interactions', 0)}")
    print(f"   Failed Interactions: {interactor_stats.get('failed_interactions', 0)}")
    print(f"   Fallback Usage: {interactor_stats.get('fallback_usage', 0)}")
    print(f"   Average Response Time: {interactor_stats.get('average_response_time', 0):.2f}s")
    
    if 'success_rate' in interactor_stats:
        print(f"   Success Rate: {interactor_stats['success_rate']:.2%}")
    
    if verbose and 'interaction_type_distribution' in interactor_stats:
        print(f"\n📈 Interaction Type Distribution:")
        for interaction_type, count in interactor_stats['interaction_type_distribution'].items():
            print(f"   {interaction_type}: {count}")
    
    if verbose and 'response_type_distribution' in interactor_stats:
        print(f"\n🎯 Response Type Distribution:")
        for response_type, count in interactor_stats['response_type_distribution'].items():
            print(f"   {response_type}: {count}")
    
    # Chat Scanner Statistics
    scanner_stats = scanner.get_chat_statistics()
    print(f"\n📱 Chat Scanner Statistics:")
    print(f"   Total Messages: {scanner_stats.get('total_messages', 0)}")
    print(f"   NPC Messages: {scanner_stats.get('npc_messages', 0)}")
    print(f"   Quest Messages: {scanner_stats.get('quest_messages', 0)}")
    print(f"   Trainer Messages: {scanner_stats.get('trainer_messages', 0)}")
    print(f"   Terminal Messages: {scanner_stats.get('terminal_messages', 0)}")
    print(f"   Vendor Messages: {scanner_stats.get('vendor_messages', 0)}")
    print(f"   Messages Requiring Response: {scanner_stats.get('response_required', 0)}")
    
    if 'npc_message_rate' in scanner_stats:
        print(f"   NPC Message Rate: {scanner_stats['npc_message_rate']:.2%}")
    
    if 'response_rate' in scanner_stats:
        print(f"   Response Rate: {scanner_stats['response_rate']:.2%}")
    
    if verbose and 'message_type_distribution' in scanner_stats:
        print(f"\n📈 Message Type Distribution:")
        for message_type, count in scanner_stats['message_type_distribution'].items():
            print(f"   {message_type}: {count}")


def test_ocr_parsing(scanner: ChatboxScanner, text: str, verbose: bool):
    """Test OCR parsing with sample text."""
    print("🔍 Testing OCR Parsing")
    print("-" * 40)
    print(f"Sample Text: {text}")
    
    # Parse message
    message = scanner.parse_single_message(text)
    if message:
        print(f"\n✅ Parsing Results:")
        print(f"   Sender: {message.sender}")
        print(f"   Type: {message.message_type.value}")
        print(f"   Content: {message.content}")
        print(f"   Requires Response: {message.requires_response}")
        print(f"   Confidence: {message.confidence:.2f}")
        
        if verbose:
            print(f"\n📋 Detailed Analysis:")
            print(f"   Text Length: {len(text)} characters")
            print(f"   Message Type: {message.message_type.value}")
            print(f"   Response Required: {message.requires_response}")
    else:
        print("❌ Failed to parse message")


def list_fallback_sequences(interactor: NPCInteractor, verbose: bool):
    """List all fallback sequences."""
    print("🔄 Fallback Sequences")
    print("-" * 40)
    
    fallback_sequences = interactor.config.get("fallback_sequences", {})
    
    if fallback_sequences:
        for interaction_type, sequence in fallback_sequences.items():
            print(f"   {interaction_type.title()}: {sequence}")
    else:
        print("   No fallback sequences configured")
    
    if verbose:
        print(f"\n📋 Configuration Details:")
        print(f"   Fallback Delay: {interactor.config.get('fallback_delay', 0.5)}s")
        print(f"   Max Retries: {interactor.config.get('max_retries', 3)}")


def test_fallback_sequence(interactor: NPCInteractor, interaction_type: str, verbose: bool):
    """Test fallback sequence for interaction type."""
    print(f"🔄 Testing Fallback Sequence: {interaction_type}")
    print("-" * 40)
    
    try:
        interaction_enum = InteractionType(interaction_type)
        success = interactor.execute_fallback_sequence(interaction_enum)
        
        if success:
            print("✅ Fallback sequence executed successfully")
        else:
            print("❌ Fallback sequence failed")
        
        if verbose:
            sequence = interactor.config.get("fallback_sequences", {}).get(interaction_type, [])
            print(f"   Sequence: {sequence}")
            print(f"   Delay: {interactor.config.get('fallback_delay', 0.5)}s")
    
    except ValueError:
        print(f"❌ Invalid interaction type: {interaction_type}")
        print(f"   Valid types: {[t.value for t in InteractionType]}")


def clear_history(interactor: NPCInteractor, scanner: ChatboxScanner, verbose: bool):
    """Clear interaction and chat history."""
    print("🗑️  Clearing History")
    print("-" * 40)
    
    # Clear NPC interaction history
    interactor.clear_history()
    print("✅ NPC interaction history cleared")
    
    # Clear chat scanner history
    scanner.clear_history()
    print("✅ Chat scanner history cleared")
    
    if verbose:
        print(f"\n📋 Statistics Reset:")
        print(f"   NPC Interactions: 0")
        print(f"   Chat Messages: 0")
        print(f"   All counters reset to zero")


if __name__ == "__main__":
    main() 