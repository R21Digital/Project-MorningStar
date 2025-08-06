"""
Experimental Dialogue NLU for Quest Intent Parsing (Batch 052)

- Extracts quest-related intent and slot information from NPC dialogues.
- Intents: start_quest, complete_quest, decline_quest, complete_quest
- Uses HuggingFace transformers pipeline for zero/few-shot intent classification.
- Includes training data, inference, and test accuracy function.
"""

from typing import List, Dict, Any
import random

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

# --- Example training data (expand as needed) ---
TRAINING_DATA = [
    # Start quest
    {"text": "Would you help me recover my lost artifact?", "intent": "start_quest"},
    {"text": "I have a task for you, are you interested?", "intent": "start_quest"},
    {"text": "Brave adventurer, will you accept this mission?", "intent": "start_quest"},
    {"text": "I need your help. Will you take this quest?", "intent": "start_quest"},
    {"text": "Can you assist me with a problem?", "intent": "start_quest"},
    {"text": "Would you like to begin the quest?", "intent": "start_quest"},
    # Complete quest
    {"text": "Thank you for completing the task!", "intent": "complete_quest"},
    {"text": "You have done well. Here is your reward.", "intent": "complete_quest"},
    {"text": "Congratulations, you have finished the quest.", "intent": "complete_quest"},
    {"text": "You have my gratitude. Quest complete!", "intent": "complete_quest"},
    {"text": "Here is your payment for a job well done.", "intent": "complete_quest"},
    # Decline quest
    {"text": "I'm sorry, I can't help you right now.", "intent": "decline_quest"},
    {"text": "No, I am not interested.", "intent": "decline_quest"},
    {"text": "Maybe another time.", "intent": "decline_quest"},
    {"text": "I have to refuse your offer.", "intent": "decline_quest"},
    {"text": "Not today, thank you.", "intent": "decline_quest"},
]

INTENTS = ["start_quest", "complete_quest", "decline_quest"]

# --- NLU Model (Zero/Few-shot using transformers pipeline) ---
class DialogueNLU:
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        if pipeline is None:
            raise ImportError("transformers is not installed. Please install transformers to use DialogueNLU.")
        self.model_name = model_name
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.intents = INTENTS

    def predict_intent(self, text: str) -> Dict[str, Any]:
        """Predict the intent of a dialogue string."""
        result = self.classifier(text, self.intents)
        # result['labels'] is sorted by score
        return {
            "intent": result["labels"][0],
            "score": result["scores"][0],
            "all_scores": dict(zip(result["labels"], result["scores"]))
        }

    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.predict_intent(t) for t in texts]

# --- Slot Extraction Stub (expandable) ---
def extract_slots(text: str) -> Dict[str, str]:
    """Stub for slot extraction (e.g., quest name, item, NPC)."""
    # For now, just a placeholder
    return {}

# --- Test Accuracy Function ---
def test_nlu_accuracy(nlu: DialogueNLU, test_data: List[Dict[str, str]] = None, verbose: bool = True) -> float:
    """Test classification accuracy on provided data."""
    if test_data is None:
        test_data = TRAINING_DATA
    correct = 0
    for sample in test_data:
        pred = nlu.predict_intent(sample["text"])
        if pred["intent"] == sample["intent"]:
            correct += 1
        elif verbose:
            print(f"FAIL: '{sample['text']}' → predicted: {pred['intent']} (score={pred['score']:.2f}), expected: {sample['intent']}")
    accuracy = correct / len(test_data)
    if verbose:
        print(f"NLU accuracy: {accuracy*100:.1f}% ({correct}/{len(test_data)})")
    return accuracy

# --- Session Quest Log Integration (stub) ---
def store_intent_in_session(session_log: List[Dict[str, Any]], text: str, intent: str, slots: Dict[str, str] = None):
    """Store extracted intent and slots into a session quest log (append to list)."""
    entry = {
        "text": text,
        "intent": intent,
        "slots": slots or {},
    }
    session_log.append(entry)

# --- Main demo/test ---
if __name__ == "__main__":
    print("[Batch 052] Experimental Dialogue NLU Demo\n")
    nlu = DialogueNLU()
    print("Testing on training data:")
    test_nlu_accuracy(nlu)
    
    # Example: classify a new dialogue
    example = "I have a dangerous job for you, are you up for it?"
    result = nlu.predict_intent(example)
    print(f"\nExample: '{example}'\nPredicted intent: {result['intent']} (score={result['score']:.2f})")
    
    # Example: store in session log
    session_log = []
    store_intent_in_session(session_log, example, result['intent'], extract_slots(example))
    print(f"\nSession log entry: {session_log[-1]}")