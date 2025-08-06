"""
Demo for Batch 052 - Rasa Evaluation for NPC and Quest Intent Parsing

This demo showcases the experimental NLU system for extracting quest-related
intents and slot information from NPC dialogues. It demonstrates:

- Intent classification for various dialogue types
- Slot extraction (NPC names, quest names, locations, rewards)
- Training data management and accuracy evaluation
- Session integration for quest logs
- Real-world dialogue examples from SWGR Legacy NPCs
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

from experimental.dialogue_nlu import (
    IntentType, SlotType, IntentResult, TrainingExample,
    get_dialogue_nlu, process_dialogue, add_training_example,
    evaluate_accuracy, get_session_summary, set_session
)


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('demo_batch_052_dialogue_nlu.log'),
            logging.StreamHandler()
        ]
    )


def create_training_data() -> List[Tuple[str, IntentType]]:
    """Create comprehensive training data for the NLU system."""
    training_examples = [
        # Start Quest Examples
        ("I have a special opportunity for someone like you. Are you interested in learning about your Legacy?", IntentType.START_QUEST),
        ("There's something unique about you. Would you like to discover your true potential?", IntentType.START_QUEST),
        ("I sense the Legacy within you. Would you like to begin your journey of discovery?", IntentType.START_QUEST),
        ("I have a job that needs doing...", IntentType.START_QUEST),
        ("There's something I need help with.", IntentType.START_QUEST),
        ("I could use someone like you.", IntentType.START_QUEST),
        ("Looking for a quest to complete?", IntentType.START_QUEST),
        ("Need help with a mission?", IntentType.START_QUEST),
        ("I have a task for you.", IntentType.START_QUEST),
        
        # Complete Quest Examples
        ("Excellent work! You've taken your first step on the path of Legacy.", IntentType.COMPLETE_QUEST),
        ("Outstanding work! You've proven yourself worthy of the Legacy training.", IntentType.COMPLETE_QUEST),
        ("Magnificent! Your potential is even greater than I imagined.", IntentType.COMPLETE_QUEST),
        ("Quest completed successfully!", IntentType.COMPLETE_QUEST),
        ("Mission accomplished!", IntentType.COMPLETE_QUEST),
        ("Task finished!", IntentType.COMPLETE_QUEST),
        ("You've done well.", IntentType.COMPLETE_QUEST),
        ("Here's your reward.", IntentType.COMPLETE_QUEST),
        
        # Decline Quest Examples
        ("I understand. The path of Legacy is not for everyone. Perhaps another time.", IntentType.DECLINE_QUEST),
        ("Very well. The choice is yours. The Legacy will wait for when you're ready.", IntentType.DECLINE_QUEST),
        ("As you wish. The potential remains within you, should you change your mind.", IntentType.DECLINE_QUEST),
        ("Not right now, sorry.", IntentType.DECLINE_QUEST),
        ("I have other things to do.", IntentType.DECLINE_QUEST),
        ("Maybe another time.", IntentType.DECLINE_QUEST),
        ("I'll pass on this one.", IntentType.DECLINE_QUEST),
        ("Not interested.", IntentType.DECLINE_QUEST),
        ("I have other priorities.", IntentType.DECLINE_QUEST),
        
        # Quest Progress Examples
        ("How is your training coming along?", IntentType.QUEST_PROGRESS),
        ("Are you making progress with your Legacy awakening?", IntentType.QUEST_PROGRESS),
        ("I'm working on it.", IntentType.QUEST_PROGRESS),
        ("Making progress.", IntentType.QUEST_PROGRESS),
        ("Still on the case.", IntentType.QUEST_PROGRESS),
        
        # Greeting Examples
        ("Welcome, traveler! I am Yevin Rook, and I sense great potential in you.", IntentType.GREETING),
        ("Ah, a new face in Mos Eisley! I am Yevin Rook, and I have a feeling about you.", IntentType.GREETING),
        ("Greetings, young one. I am Yevin Rook, and I believe you are destined for greatness.", IntentType.GREETING),
        ("Hello there!", IntentType.GREETING),
        ("Welcome, traveler.", IntentType.GREETING),
        ("What can I do for you?", IntentType.GREETING),
        
        # Farewell Examples
        ("May the Legacy guide your path, young one.", IntentType.FAREWELL),
        ("Remember, your potential is limitless. Use it wisely.", IntentType.FAREWELL),
        ("The desert will teach you much. Return when you're ready for more training.", IntentType.FAREWELL),
        ("Safe travels, and may the Force be with you.", IntentType.FAREWELL),
        ("Safe travels!", IntentType.FAREWELL),
        ("May the Force be with you.", IntentType.FAREWELL),
        ("Come back anytime.", IntentType.FAREWELL),
        
        # Training Offer Examples
        ("Would you like to learn some basic combat techniques?", IntentType.TRAINING_OFFER),
        ("I can teach you essential survival skills. Are you interested?", IntentType.TRAINING_OFFER),
        ("There's much to learn about the Legacy. Shall we begin with the fundamentals?", IntentType.TRAINING_OFFER),
        ("I can teach you combat techniques.", IntentType.TRAINING_OFFER),
        ("Want to improve your fighting skills?", IntentType.TRAINING_OFFER),
        ("I have training available.", IntentType.TRAINING_OFFER),
        ("I can teach you medical skills.", IntentType.TRAINING_OFFER),
        ("Want to learn healing techniques?", IntentType.TRAINING_OFFER),
        ("Medical training is available.", IntentType.TRAINING_OFFER),
        
        # Training Accept Examples
        ("I'd like to learn.", IntentType.TRAINING_ACCEPT),
        ("Teach me what you know.", IntentType.TRAINING_ACCEPT),
        ("I'm ready to train.", IntentType.TRAINING_ACCEPT),
        ("I want to learn healing.", IntentType.TRAINING_ACCEPT),
        ("Teach me medical skills.", IntentType.TRAINING_ACCEPT),
        ("I'm interested in medicine.", IntentType.TRAINING_ACCEPT),
        ("Excellent! Let's start with the basics of combat and survival.", IntentType.TRAINING_ACCEPT),
        ("Perfect! I'll teach you everything you need to know about the Legacy.", IntentType.TRAINING_ACCEPT),
        ("Wonderful! Your training begins immediately.", IntentType.TRAINING_ACCEPT),
        
        # Training Decline Examples
        ("Not right now.", IntentType.TRAINING_DECLINE),
        ("I'll think about it.", IntentType.TRAINING_DECLINE),
        ("Maybe later.", IntentType.TRAINING_DECLINE),
        ("Not interested right now.", IntentType.TRAINING_DECLINE),
        ("I'll consider it.", IntentType.TRAINING_DECLINE),
        ("Maybe another time.", IntentType.TRAINING_DECLINE),
        ("I understand. Training can be intense. Take your time.", IntentType.TRAINING_DECLINE),
        ("Very well. The training will be here when you're ready.", IntentType.TRAINING_DECLINE),
        ("As you wish. The Legacy training awaits your return.", IntentType.TRAINING_DECLINE),
        
        # Collection Offer Examples
        ("I need someone to collect rare items for my collection.", IntentType.COLLECTION_OFFER),
        ("There are valuable materials to gather in the desert.", IntentType.COLLECTION_OFFER),
        ("I'm looking for someone to help with a collection quest.", IntentType.COLLECTION_OFFER),
        ("I have a special collection that needs rare items.", IntentType.COLLECTION_OFFER),
        ("Would you help me gather some materials?", IntentType.COLLECTION_OFFER),
        
        # Collection Accept Examples
        ("I'll help you collect those items.", IntentType.COLLECTION_ACCEPT),
        ("I'm interested in gathering materials.", IntentType.COLLECTION_ACCEPT),
        ("I'll take on the collection quest.", IntentType.COLLECTION_ACCEPT),
        ("I want to help with your collection.", IntentType.COLLECTION_ACCEPT),
        ("I'll gather the materials you need.", IntentType.COLLECTION_ACCEPT),
        
        # Collection Decline Examples
        ("Not interested in collecting right now.", IntentType.COLLECTION_DECLINE),
        ("I'll pass on the collection quest.", IntentType.COLLECTION_DECLINE),
        ("I have other priorities than collecting.", IntentType.COLLECTION_DECLINE),
        ("Maybe another time for collection.", IntentType.COLLECTION_DECLINE),
        ("I'm not really into collecting items.", IntentType.COLLECTION_DECLINE)
    ]
    
    return training_examples


def create_test_dialogues() -> List[Dict[str, Any]]:
    """Create test dialogues for demonstration."""
    return [
        {
            "npc": "Yevin Rook",
            "text": "Welcome, traveler! I am Yevin Rook, and I sense great potential in you.",
            "expected_intent": IntentType.GREETING,
            "expected_slots": {"npc_name": "Yevin"}
        },
        {
            "npc": "Yevin Rook",
            "text": "I have a special opportunity for someone like you. Are you interested in learning about your Legacy?",
            "expected_intent": IntentType.START_QUEST,
            "expected_slots": {"npc_name": "Yevin", "quest_name": "Legacy training"}
        },
        {
            "npc": "Player",
            "text": "I'll help you with that quest.",
            "expected_intent": IntentType.START_QUEST,
            "expected_slots": {}
        },
        {
            "npc": "Yevin Rook",
            "text": "Excellent! Your journey begins now. Let me teach you the basics of survival.",
            "expected_intent": IntentType.TRAINING_ACCEPT,
            "expected_slots": {"npc_name": "Yevin"}
        },
        {
            "npc": "Yevin Rook",
            "text": "Outstanding work! You've taken your first step on the path of Legacy.",
            "expected_intent": IntentType.COMPLETE_QUEST,
            "expected_slots": {"npc_name": "Yevin"}
        },
        {
            "npc": "Merchant",
            "text": "I have a job that needs doing in Mos Eisley. Reward: 500 credits.",
            "expected_intent": IntentType.START_QUEST,
            "expected_slots": {"npc_name": "Merchant", "location": "Mos", "reward": "500 credits"}
        },
        {
            "npc": "Combat Trainer",
            "text": "I can teach you combat techniques. Want to improve your fighting skills?",
            "expected_intent": IntentType.TRAINING_OFFER,
            "expected_slots": {"npc_name": "Combat"}
        },
        {
            "npc": "Player",
            "text": "Not right now, I have other things to do.",
            "expected_intent": IntentType.DECLINE_QUEST,
            "expected_slots": {}
        },
        {
            "npc": "Collection Master",
            "text": "I need someone to collect rare crystals in the desert. 1000 XP reward.",
            "expected_intent": IntentType.COLLECTION_OFFER,
            "expected_slots": {"npc_name": "Collection", "quest_name": "rare crystals", "reward": "1000 XP"}
        },
        {
            "npc": "Player",
            "text": "I'll help you gather those materials.",
            "expected_intent": IntentType.COLLECTION_ACCEPT,
            "expected_slots": {}
        }
    ]


def demo_basic_intent_classification():
    """Demo basic intent classification functionality."""
    print("\n" + "="*60)
    print("DEMO: Basic Intent Classification")
    print("="*60)
    
    # Get NLU instance
    nlu = get_dialogue_nlu()
    
    # Test dialogues
    test_dialogues = create_test_dialogues()
    
    print("Processing test dialogues...")
    for i, dialogue in enumerate(test_dialogues, 1):
        print(f"\n{i}. NPC: {dialogue['npc']}")
        print(f"   Text: {dialogue['text']}")
        
        # Process dialogue
        result = process_dialogue(dialogue['text'], dialogue['npc'])
        
        print(f"   Intent: {result.intent.value}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Slots: {result.slots}")
        
        # Check if prediction matches expected
        if result.intent == dialogue['expected_intent']:
            print(f"   ✓ Correct intent prediction")
        else:
            print(f"   ✗ Expected: {dialogue['expected_intent'].value}")
        
        # Check slot extraction
        if dialogue['expected_slots']:
            for slot_name, expected_value in dialogue['expected_slots'].items():
                if slot_name in result.slots:
                    print(f"   ✓ Slot '{slot_name}': {result.slots[slot_name]}")
                else:
                    print(f"   ✗ Missing slot '{slot_name}'")


def demo_training_data_management():
    """Demo training data management."""
    print("\n" + "="*60)
    print("DEMO: Training Data Management")
    print("="*60)
    
    # Create training data
    training_examples = create_training_data()
    
    print(f"Adding {len(training_examples)} training examples...")
    
    # Add training examples
    for text, intent in training_examples:
        add_training_example(text, intent)
    
    print("Training examples added successfully!")
    
    # Show training data summary
    nlu = get_dialogue_nlu()
    classifier = nlu.classifier
    
    print(f"\nTraining data summary:")
    print(f"  Total examples: {len(classifier.training_examples)}")
    
    # Count examples by intent
    intent_counts = {}
    for example in classifier.training_examples:
        intent_counts[example.intent.value] = intent_counts.get(example.intent.value, 0) + 1
    
    print(f"  Examples by intent:")
    for intent, count in sorted(intent_counts.items()):
        print(f"    {intent}: {count}")


def demo_accuracy_evaluation():
    """Demo accuracy evaluation on test data."""
    print("\n" + "="*60)
    print("DEMO: Accuracy Evaluation")
    print("="*60)
    
    # Create test examples
    test_examples = [
        ("I have a quest for you", IntentType.START_QUEST),
        ("Quest completed!", IntentType.COMPLETE_QUEST),
        ("Not interested", IntentType.DECLINE_QUEST),
        ("Hello there!", IntentType.GREETING),
        ("Goodbye!", IntentType.FAREWELL),
        ("I can teach you skills", IntentType.TRAINING_OFFER),
        ("I want to learn", IntentType.TRAINING_ACCEPT),
        ("Not right now", IntentType.TRAINING_DECLINE),
        ("Collect rare items", IntentType.COLLECTION_OFFER),
        ("I'll help collect", IntentType.COLLECTION_ACCEPT),
        ("Pass on collection", IntentType.COLLECTION_DECLINE),
        ("How is progress?", IntentType.QUEST_PROGRESS),
        ("Working on it", IntentType.QUEST_PROGRESS),
        ("Mission accomplished", IntentType.COMPLETE_QUEST),
        ("I decline the quest", IntentType.DECLINE_QUEST)
    ]
    
    print(f"Evaluating accuracy on {len(test_examples)} test examples...")
    
    # Evaluate accuracy
    metrics = evaluate_accuracy(test_examples)
    
    print(f"\nAccuracy Results:")
    print(f"  Overall Accuracy: {metrics['overall_accuracy']:.2%}")
    print(f"  Total Examples: {metrics['total_examples']}")
    print(f"  Correct Predictions: {metrics['correct_predictions']}")
    
    print(f"\nPer-Intent Accuracy:")
    for intent, accuracy in metrics['per_intent_accuracy'].items():
        print(f"  {intent}: {accuracy:.2%}")


def demo_session_integration():
    """Demo session integration and quest log storage."""
    print("\n" + "="*60)
    print("DEMO: Session Integration")
    print("="*60)
    
    # Set up session
    session_id = "demo_session_052"
    set_session(session_id)
    
    print(f"Set session: {session_id}")
    
    # Simulate a quest dialogue session
    dialogue_session = [
        ("Yevin Rook", "Welcome, traveler! I am Yevin Rook, and I sense great potential in you."),
        ("Player", "Hello! I'm interested in learning more."),
        ("Yevin Rook", "I have a special opportunity for someone like you. Are you interested in learning about your Legacy?"),
        ("Player", "Yes, I'll help you with that quest."),
        ("Yevin Rook", "Excellent! Your journey begins now. Let me teach you the basics of survival."),
        ("Player", "I'm ready to train."),
        ("Yevin Rook", "Outstanding work! You've taken your first step on the path of Legacy."),
        ("Player", "Thank you for the training."),
        ("Yevin Rook", "May the Legacy guide your path, young one.")
    ]
    
    print("\nProcessing dialogue session...")
    
    for npc_name, text in dialogue_session:
        print(f"\n  {npc_name}: {text}")
        
        # Process dialogue
        result = process_dialogue(text, npc_name)
        
        print(f"    Intent: {result.intent.value} (confidence: {result.confidence:.2f})")
        if result.slots:
            print(f"    Slots: {result.slots}")
    
    # Get session summary
    summary = get_session_summary()
    
    print(f"\nSession Summary:")
    print(f"  Total Intents: {summary['total_intents']}")
    print(f"  Average Confidence: {summary['average_confidence']:.2f}")
    print(f"  Intent Distribution:")
    for intent, count in summary['intent_distribution'].items():
        print(f"    {intent}: {count}")


def demo_slot_extraction():
    """Demo slot extraction capabilities."""
    print("\n" + "="*60)
    print("DEMO: Slot Extraction")
    print("="*60)
    
    # Test cases for slot extraction
    slot_test_cases = [
        {
            "text": "I am Yevin Rook, and I have a quest for you.",
            "description": "NPC name extraction"
        },
        {
            "text": "I need help with a mission: Defeat the Bounty Hunter",
            "description": "Quest name extraction"
        },
        {
            "text": "Go to Mos Eisley and collect the rare crystals.",
            "description": "Location extraction"
        },
        {
            "text": "Complete this task and receive 1000 credits reward.",
            "description": "Reward extraction"
        },
        {
            "text": "My name is Combat Trainer. I can teach you skills in Tatooine.",
            "description": "Multiple slot extraction"
        },
        {
            "text": "I am Yevin Rook. I have a quest: Legacy Training. Go to Mos Eisley for 500 XP reward.",
            "description": "Complex slot extraction"
        }
    ]
    
    print("Testing slot extraction...")
    
    for i, test_case in enumerate(slot_test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Text: {test_case['text']}")
        
        # Process dialogue
        result = process_dialogue(test_case['text'])
        
        print(f"   Intent: {result.intent.value}")
        print(f"   Extracted Slots:")
        for slot_name, slot_value in result.slots.items():
            print(f"     {slot_name}: {slot_value}")


def demo_error_handling():
    """Demo error handling and edge cases."""
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    # Test edge cases
    edge_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("Hello", "Simple greeting"),
        ("This is a very long dialogue that doesn't match any specific patterns but contains some keywords like quest and training", "Long complex text"),
        ("123 456 789", "Numbers only"),
        ("!@#$%^&*()", "Special characters only"),
        ("I have a quest quest quest quest", "Repetitive keywords"),
        ("The quick brown fox jumps over the lazy dog", "Unrelated text")
    ]
    
    print("Testing edge cases...")
    
    for text, description in edge_cases:
        print(f"\n  {description}")
        print(f"  Text: '{text}'")
        
        # Process dialogue
        result = process_dialogue(text)
        
        print(f"  Intent: {result.intent.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Slots: {result.slots}")


def demo_performance_metrics():
    """Demo performance metrics and analysis."""
    print("\n" + "="*60)
    print("DEMO: Performance Metrics")
    print("="*60)
    
    nlu = get_dialogue_nlu()
    classifier = nlu.classifier
    
    # Get classification history
    history = classifier.get_classification_history()
    
    print(f"Classification History:")
    print(f"  Total Classifications: {len(history)}")
    
    if history:
        # Calculate metrics
        avg_confidence = sum(r.confidence for r in history) / len(history)
        intent_distribution = {}
        for result in history:
            intent_distribution[result.intent.value] = intent_distribution.get(result.intent.value, 0) + 1
        
        print(f"  Average Confidence: {avg_confidence:.2f}")
        print(f"  Intent Distribution:")
        for intent, count in sorted(intent_distribution.items()):
            percentage = (count / len(history)) * 100
            print(f"    {intent}: {count} ({percentage:.1f}%)")
        
        # Show recent classifications
        print(f"\n  Recent Classifications:")
        for result in history[-5:]:  # Last 5
            print(f"    {result.intent.value} ({result.confidence:.2f}): {result.raw_text[:50]}...")
    
    # Get accuracy metrics
    metrics = classifier.get_accuracy_metrics()
    if metrics:
        print(f"\n  Accuracy Metrics:")
        print(f"    Overall Accuracy: {metrics.get('overall_accuracy', 0):.2%}")
        print(f"    Total Examples: {metrics.get('total_examples', 0)}")
        print(f"    Correct Predictions: {metrics.get('correct_predictions', 0)}")


def main():
    """Run the complete demo."""
    print("MS11 Batch 052 - Rasa Evaluation for NPC and Quest Intent Parsing Demo")
    print("="*60)
    
    setup_logging()
    
    try:
        # Run all demos
        demo_basic_intent_classification()
        demo_training_data_management()
        demo_accuracy_evaluation()
        demo_session_integration()
        demo_slot_extraction()
        demo_error_handling()
        demo_performance_metrics()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        
        # Final summary
        final_summary = get_session_summary()
        print(f"Final Summary:")
        print(f"  Total Intents Processed: {final_summary['total_intents']}")
        print(f"  Average Confidence: {final_summary['average_confidence']:.2f}")
        print(f"  Intent Types: {len(final_summary['intent_distribution'])}")
        
        # Save demo results
        with open('demo_batch_052_results.json', 'w') as f:
            json.dump(final_summary, f, indent=2)
        print(f"\nDemo results saved to: demo_batch_052_results.json")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)


if __name__ == "__main__":
    main() 