#!/usr/bin/env python3
"""
MS11 Batch 091 - AI Assistant Demo

This script demonstrates the new AI assistant functionality,
including data ingestion, content filtering, and response generation.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.ai_assistant import ai_assistant, AIDataIngestion, ContentFilter, AIDroidPersonality
from core.chat_session_manager import chat_session_manager

def demonstrate_data_ingestion():
    """Demonstrate data ingestion capabilities."""
    print("Demonstrating AI Assistant Data Ingestion...")
    print("=" * 50)
    
    # Test data ingestion
    ingestion = AIDataIngestion()
    ingested_data = ingestion.ingest_all_data()
    
    print(f"✓ Ingested {len(ingested_data)} data categories:")
    for category, data in ingested_data.items():
        if isinstance(data, dict):
            print(f"  - {category}: {len(data)} items")
        elif isinstance(data, list):
            print(f"  - {category}: {len(data)} items")
        else:
            print(f"  - {category}: {type(data).__name__}")
    
    print()

def demonstrate_content_filtering():
    """Demonstrate content filtering capabilities."""
    print("Demonstrating Content Filtering...")
    print("=" * 50)
    
    filter_obj = ContentFilter()
    
    # Test messages
    test_messages = [
        "Where can I find a Marksman trainer?",
        "How do I configure my MS11 bot?",
        "Tell me about quests on Tatooine",
        "What automation settings should I use?",
        "How do I travel between planets?",
        "My bot is stuck, what should I do?"
    ]
    
    for message in test_messages:
        is_sensitive = filter_obj.contains_sensitive_content(message)
        sanitized = filter_obj.sanitize_content(message)
        
        status = "❌ BLOCKED" if is_sensitive else "✅ ALLOWED"
        print(f"{status}: {message}")
        if is_sensitive:
            print(f"  Sanitized: {sanitized}")
        print()

def demonstrate_droid_personality():
    """Demonstrate droid personality features."""
    print("Demonstrating AZ-L0N Droid Personality...")
    print("=" * 50)
    
    personality = AIDroidPersonality()
    
    print(f"✓ Droid Name: {personality.name}")
    print(f"✓ Title: {personality.title}")
    print(f"✓ Personality Traits: {', '.join(personality.personality_traits)}")
    print()
    
    print("Sample Greetings:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_greeting()}")
    print()
    
    print("Sample Farewells:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_farewell()}")
    print()
    
    print("Sample Confused Responses:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_confused_response()}")
    print()

def demonstrate_ai_responses():
    """Demonstrate AI response generation."""
    print("Demonstrating AI Response Generation...")
    print("=" * 50)
    
    # Test questions
    test_questions = [
        "Where can I find a Marksman trainer?",
        "Tell me about quests on Tatooine",
        "What professions are available?",
        "Tell me about the Rebel Alliance",
        "How do I travel between planets?",
        "What races can I play as?",
        "Tell me about Naboo"
    ]
    
    for question in test_questions:
        print(f"Q: {question}")
        response = ai_assistant.process_message(question)
        print(f"A: {response}")
        print()

def demonstrate_chat_sessions():
    """Demonstrate chat session management."""
    print("Demonstrating Chat Session Management...")
    print("=" * 50)
    
    # Create a test session
    session_id = chat_session_manager.create_session("demo_user", "general")
    print(f"✓ Created session: {session_id}")
    
    # Send some test messages
    test_messages = [
        "Where can I find a Marksman trainer?",
        "Tell me about quests on Tatooine",
        "What professions are available?"
    ]
    
    for message in test_messages:
        response = chat_session_manager.process_user_message(session_id, message)
        print(f"User: {message}")
        print(f"AZ-L0N: {response}")
        print()
    
    # Get session history
    history = chat_session_manager.get_session_history(session_id)
    print(f"✓ Session history: {len(history)} messages")
    
    # Get session stats
    stats = chat_session_manager.get_session_stats()
    print(f"✓ Chat stats: {stats['active_sessions']} active, {stats['total_sessions']} total")
    
    # Clean up
    chat_session_manager.delete_session(session_id)
    print(f"✓ Cleaned up session: {session_id}")
    print()

def demonstrate_sensitive_content_handling():
    """Demonstrate how sensitive content is handled."""
    print("Demonstrating Sensitive Content Handling...")
    print("=" * 50)
    
    sensitive_messages = [
        "How do I configure my MS11 bot?",
        "What automation settings should I use?",
        "My bot is stuck, what should I do?",
        "Tell me about third-party tools",
        "How do I use macros?"
    ]
    
    for message in sensitive_messages:
        response = ai_assistant.process_message(message)
        print(f"Input: {message}")
        print(f"Response: {response}")
        print()

def demonstrate_api_endpoints():
    """Demonstrate API endpoint functionality."""
    print("Demonstrating API Endpoints...")
    print("=" * 50)
    
    # Test session creation
    session_id = chat_session_manager.create_session("api_test", "general")
    print(f"✓ Created session via API: {session_id}")
    
    # Test message sending
    response = chat_session_manager.process_user_message(session_id, "Where can I find a Marksman trainer?")
    print(f"✓ Sent message, got response: {response[:50]}...")
    
    # Test session listing
    sessions = chat_session_manager.list_sessions(limit=5)
    print(f"✓ Listed {len(sessions)} sessions")
    
    # Clean up
    chat_session_manager.delete_session(session_id)
    print(f"✓ Cleaned up API test session")
    print()

def main():
    """Main demonstration function."""
    print("MS11 Batch 091 - AI Assistant Demo")
    print("=" * 60)
    print()
    
    # Ensure data directories exist
    os.makedirs("data/ai_chat_sessions", exist_ok=True)
    
    # Run demonstrations
    demonstrate_data_ingestion()
    demonstrate_content_filtering()
    demonstrate_droid_personality()
    demonstrate_ai_responses()
    demonstrate_chat_sessions()
    demonstrate_sensitive_content_handling()
    demonstrate_api_endpoints()
    
    print("=" * 60)
    print("Demo completed!")
    print()
    print("Next steps:")
    print("1. Start the dashboard: python dashboard/app.py")
    print("2. Visit http://localhost:8000/ai-chat")
    print("3. Chat with AZ-L0N, your protocol droid assistant!")
    print()
    print("API Endpoints:")
    print("- POST /api/ai-chat/session - Create new chat session")
    print("- POST /api/ai-chat/session/<id>/message - Send message")
    print("- GET /api/ai-chat/session/<id>/history - Get chat history")
    print("- GET /api/ai-chat/sessions - List all sessions")
    print("- DELETE /api/ai-chat/session/<id> - Delete session")
    print("- GET /api/ai-chat/stats - Get chat statistics")

if __name__ == "__main__":
    main() 