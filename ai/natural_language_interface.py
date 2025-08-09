"""
MS11 Natural Language Interface System
Advanced NLP for voice commands, chat interpretation, and conversational automation control
"""

import asyncio
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Callable, Union, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import threading
import difflib
import hashlib

try:
    import spacy
    import spacy.cli
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    TEXT_TO_SPEECH_AVAILABLE = True
except ImportError:
    TEXT_TO_SPEECH_AVAILABLE = False

from core.structured_logging import StructuredLogger
from core.observability_integration import get_observability_manager, trace_gaming_operation

# Initialize logger
logger = StructuredLogger("natural_language_interface")

class CommandCategory(Enum):
    """Categories of natural language commands"""
    COMBAT = "combat"
    MOVEMENT = "movement"
    INVENTORY = "inventory"
    QUEST = "quest"
    SOCIAL = "social"
    CRAFTING = "crafting"
    TRADE = "trade"
    SYSTEM = "system"
    INFO = "info"
    AUTOMATION = "automation"

class IntentType(Enum):
    """Types of user intents"""
    START_ACTION = "start_action"
    STOP_ACTION = "stop_action"
    STATUS_QUERY = "status_query"
    CONFIGURATION = "configuration"
    QUESTION = "question"
    COMMAND = "command"
    CONFIRMATION = "confirmation"
    CANCELLATION = "cancellation"

class ResponseType(Enum):
    """Types of system responses"""
    ACKNOWLEDGMENT = "acknowledgment"
    STATUS_REPORT = "status_report"
    QUESTION = "question"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

class ConfidenceLevel(Enum):
    """NLP confidence levels"""
    LOW = "low"           # 0-50%
    MEDIUM = "medium"     # 51-75%
    HIGH = "high"         # 76-90%
    VERY_HIGH = "very_high"  # 91-100%

@dataclass
class ParsedCommand:
    """Parsed natural language command"""
    original_text: str
    cleaned_text: str
    intent: IntentType
    category: CommandCategory
    action: str
    parameters: Dict[str, Any]
    entities: Dict[str, str]
    confidence: float
    confidence_level: ConfidenceLevel
    timestamp: datetime
    
    def __post_init__(self):
        # Set confidence level based on score
        if self.confidence >= 0.91:
            self.confidence_level = ConfidenceLevel.VERY_HIGH
        elif self.confidence >= 0.76:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.confidence >= 0.51:
            self.confidence_level = ConfidenceLevel.MEDIUM
        else:
            self.confidence_level = ConfidenceLevel.LOW

@dataclass
class SystemResponse:
    """System response to user"""
    text: str
    response_type: ResponseType
    category: CommandCategory
    requires_confirmation: bool = False
    actions_to_take: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ConversationContext:
    """Conversation context tracking"""
    session_id: str
    user_id: str
    started_at: datetime
    last_interaction: datetime
    command_history: deque = field(default_factory=lambda: deque(maxlen=50))
    active_confirmations: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_state: str = "idle"  # idle, waiting_confirmation, executing

class CommandPatternMatcher:
    """Pattern matching for natural language commands"""
    
    def __init__(self):
        # Command patterns organized by category and intent
        self.patterns = {
            CommandCategory.COMBAT: {
                IntentType.START_ACTION: [
                    r"start (?:combat|fighting|attack)",
                    r"begin (?:combat|attack|fighting)",
                    r"attack (?:the )?(\w+)",
                    r"fight (?:the )?(\w+)",
                    r"engage (?:in )?combat",
                    r"start (?:auto )?attacking"
                ],
                IntentType.STOP_ACTION: [
                    r"stop (?:combat|fighting|attack)",
                    r"disengage",
                    r"retreat",
                    r"flee",
                    r"stop attacking",
                    r"end combat"
                ],
                IntentType.STATUS_QUERY: [
                    r"combat status",
                    r"am i fighting",
                    r"current (?:combat|fight) status",
                    r"health status",
                    r"how (?:much|low) is my health"
                ]
            },
            CommandCategory.MOVEMENT: {
                IntentType.START_ACTION: [
                    r"go to (\w+)",
                    r"move to (\w+)",
                    r"walk to (\w+)",
                    r"travel to (\w+)",
                    r"head to (\w+)",
                    r"navigate to (\w+)"
                ],
                IntentType.STOP_ACTION: [
                    r"stop (?:moving|walking)",
                    r"halt",
                    r"pause movement",
                    r"stop here"
                ],
                IntentType.STATUS_QUERY: [
                    r"where am i",
                    r"current location",
                    r"my position",
                    r"movement status"
                ]
            },
            CommandCategory.QUEST: {
                IntentType.START_ACTION: [
                    r"start quest (\w+)",
                    r"begin quest (\w+)",
                    r"do quest (\w+)",
                    r"accept quest (\w+)",
                    r"take quest (\w+)"
                ],
                IntentType.STATUS_QUERY: [
                    r"quest status",
                    r"current quests?",
                    r"what quests? (?:am i|do i have)",
                    r"quest progress",
                    r"show quests?"
                ]
            },
            CommandCategory.INVENTORY: {
                IntentType.STATUS_QUERY: [
                    r"inventory",
                    r"show (?:my )?items",
                    r"what (?:do i|items) have",
                    r"list inventory",
                    r"bag contents"
                ],
                IntentType.START_ACTION: [
                    r"use (\w+)",
                    r"equip (\w+)",
                    r"sell (\w+)",
                    r"buy (\w+)",
                    r"drop (\w+)"
                ]
            },
            CommandCategory.AUTOMATION: {
                IntentType.START_ACTION: [
                    r"start (?:auto|automation)",
                    r"begin (?:auto|automation)",
                    r"enable (?:auto|automation)",
                    r"turn on (?:auto|automation)",
                    r"activate (?:auto|automation)"
                ],
                IntentType.STOP_ACTION: [
                    r"stop (?:auto|automation)",
                    r"disable (?:auto|automation)",
                    r"turn off (?:auto|automation)",
                    r"deactivate (?:auto|automation)",
                    r"pause (?:auto|automation)"
                ],
                IntentType.STATUS_QUERY: [
                    r"(?:auto|automation) status",
                    r"is (?:auto|automation) (?:on|running|active)",
                    r"what.s (?:auto|automation) doing"
                ],
                IntentType.CONFIGURATION: [
                    r"configure (?:auto|automation)",
                    r"set (?:auto|automation) (?:to|for) (\w+)",
                    r"change (?:auto|automation) settings"
                ]
            },
            CommandCategory.SYSTEM: {
                IntentType.STATUS_QUERY: [
                    r"status",
                    r"system status",
                    r"how.?s (?:everything|it going)",
                    r"current state",
                    r"overview"
                ],
                IntentType.CONFIGURATION: [
                    r"settings",
                    r"configure",
                    r"options",
                    r"preferences"
                ],
                IntentType.COMMAND: [
                    r"help",
                    r"commands",
                    r"what can (?:you|i) do",
                    r"instructions"
                ]
            }
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            "target": r"(?:target|mob|enemy|monster) (\w+)",
            "location": r"(?:to|at|near) (\w+)",
            "item": r"(?:item|equipment|gear) (\w+)",
            "skill": r"(?:skill|ability|spell) (\w+)",
            "number": r"(\d+)",
            "duration": r"for (\d+) (?:minutes?|hours?|seconds?)"
        }
        
        # Compile patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        self.compiled_patterns = {}
        
        for category, intents in self.patterns.items():
            self.compiled_patterns[category] = {}
            for intent, patterns in intents.items():
                self.compiled_patterns[category][intent] = [
                    re.compile(pattern, re.IGNORECASE) for pattern in patterns
                ]
        
        self.compiled_entities = {
            name: re.compile(pattern, re.IGNORECASE) 
            for name, pattern in self.entity_patterns.items()
        }
    
    def match_command(self, text: str) -> Optional[Tuple[CommandCategory, IntentType, str, float]]:
        """Match text against command patterns"""
        
        best_match = None
        best_confidence = 0.0
        best_action = ""
        
        cleaned_text = self._clean_text(text)
        
        for category, intents in self.compiled_patterns.items():
            for intent, patterns in intents.items():
                for pattern in patterns:
                    match = pattern.search(cleaned_text)
                    if match:
                        # Calculate confidence based on match quality
                        match_length = len(match.group(0))
                        text_length = len(cleaned_text)
                        confidence = (match_length / text_length) * 0.8 + 0.2
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (category, intent)
                            best_action = match.group(1) if len(match.groups()) > 0 else "default"
        
        if best_match and best_confidence > 0.3:
            return (*best_match, best_action, best_confidence)
        
        return None
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from text"""
        entities = {}
        
        for entity_name, pattern in self.compiled_entities.items():
            match = pattern.search(text)
            if match:
                entities[entity_name] = match.group(1)
        
        return entities
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Expand contractions
        contractions = {
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "i'm": "i am",
            "you're": "you are",
            "what's": "what is"
        }
        
        for contraction, expansion in contractions.items():
            text = re.sub(r'\b' + contraction + r'\b', expansion, text, flags=re.IGNORECASE)
        
        return text.lower()

class NLPProcessor:
    """Advanced NLP processing using spaCy and transformers"""
    
    def __init__(self):
        self.nlp = None
        self.sentiment_pipeline = None
        self.intent_classifier = None
        self.is_initialized = False
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models"""
        try:
            # Initialize spaCy
            if SPACY_AVAILABLE:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy model 'en_core_web_sm' not found, trying to download")
                    try:
                        spacy.cli.download("en_core_web_sm")
                        self.nlp = spacy.load("en_core_web_sm")
                    except Exception as e:
                        logger.warning("Failed to download spaCy model", error=str(e))
                        self.nlp = None
            
            # Initialize transformers
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Lightweight sentiment analysis
                    self.sentiment_pipeline = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                        device=-1  # CPU only
                    )
                    
                    # Intent classification (using a general purpose model)
                    self.intent_classifier = pipeline(
                        "zero-shot-classification",
                        model="facebook/bart-large-mnli",
                        device=-1  # CPU only
                    )
                    
                except Exception as e:
                    logger.warning("Failed to initialize transformers models", error=str(e))
                    self.sentiment_pipeline = None
                    self.intent_classifier = None
            
            self.is_initialized = True
            logger.info("NLP processor initialized",
                       spacy=self.nlp is not None,
                       sentiment=self.sentiment_pipeline is not None,
                       intent=self.intent_classifier is not None)
            
        except Exception as e:
            logger.error("NLP processor initialization error", error=str(e))
    
    def analyze_intent(self, text: str) -> Tuple[IntentType, float]:
        """Analyze intent using zero-shot classification"""
        
        if not self.intent_classifier:
            # Fallback to simple keyword matching
            return self._simple_intent_analysis(text)
        
        try:
            candidate_labels = [intent.value for intent in IntentType]
            
            result = self.intent_classifier(text, candidate_labels)
            
            best_label = result['labels'][0]
            confidence = result['scores'][0]
            
            intent = IntentType(best_label)
            
            return intent, confidence
            
        except Exception as e:
            logger.error("Intent analysis error", error=str(e))
            return self._simple_intent_analysis(text)
    
    def _simple_intent_analysis(self, text: str) -> Tuple[IntentType, float]:
        """Simple keyword-based intent analysis"""
        text_lower = text.lower()
        
        # Simple keyword mapping
        intent_keywords = {
            IntentType.START_ACTION: ["start", "begin", "do", "go", "move", "attack", "use"],
            IntentType.STOP_ACTION: ["stop", "halt", "pause", "end", "quit", "cancel"],
            IntentType.STATUS_QUERY: ["status", "how", "what", "where", "show", "list"],
            IntentType.CONFIGURATION: ["set", "configure", "change", "adjust", "settings"],
            IntentType.QUESTION: ["what", "how", "why", "when", "where", "can", "help"],
            IntentType.CONFIRMATION: ["yes", "ok", "confirm", "sure", "proceed"],
            IntentType.CANCELLATION: ["no", "cancel", "abort", "never mind"]
        }
        
        best_intent = IntentType.QUESTION
        best_score = 0.0
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower) / len(keywords)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent, min(best_score + 0.3, 1.0)
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        
        if not self.nlp:
            return {}
        
        try:
            doc = self.nlp(text)
            entities = defaultdict(list)
            
            for ent in doc.ents:
                entities[ent.label_].append(ent.text)
            
            return dict(entities)
            
        except Exception as e:
            logger.error("Named entity extraction error", error=str(e))
            return {}
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of text"""
        
        if not self.sentiment_pipeline:
            # Simple keyword-based sentiment
            return self._simple_sentiment_analysis(text)
        
        try:
            result = self.sentiment_pipeline(text)[0]
            
            label = result['label'].lower()
            confidence = result['score']
            
            # Map labels to standard format
            sentiment_mapping = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral',
                'label_0': 'negative',
                'label_1': 'neutral', 
                'label_2': 'positive'
            }
            
            sentiment = sentiment_mapping.get(label, 'neutral')
            
            return sentiment, confidence
            
        except Exception as e:
            logger.error("Sentiment analysis error", error=str(e))
            return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> Tuple[str, float]:
        """Simple keyword-based sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = ["good", "great", "excellent", "awesome", "perfect", "love", "like", "happy", "thanks"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "angry", "frustrated", "wrong", "error"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive", 0.6
        elif negative_count > positive_count:
            return "negative", 0.6
        else:
            return "neutral", 0.5

class VoiceInterface:
    """Voice recognition and text-to-speech interface"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.is_listening = False
        self.voice_enabled = False
        
        self._initialize_voice_components()
    
    def _initialize_voice_components(self):
        """Initialize voice recognition and TTS"""
        try:
            # Initialize speech recognition
            if SPEECH_RECOGNITION_AVAILABLE:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                
                logger.info("Speech recognition initialized")
            
            # Initialize text-to-speech
            if TEXT_TO_SPEECH_AVAILABLE:
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS settings
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    self.tts_engine.setProperty('voice', voices[0].id)
                
                self.tts_engine.setProperty('rate', 180)  # Speed
                self.tts_engine.setProperty('volume', 0.8)  # Volume
                
                logger.info("Text-to-speech initialized")
            
            self.voice_enabled = (self.recognizer is not None or self.tts_engine is not None)
            
        except Exception as e:
            logger.error("Voice interface initialization error", error=str(e))
    
    @trace_gaming_operation("voice_recognition")
    def listen_for_command(self, timeout: float = 5.0) -> Optional[str]:
        """Listen for voice command"""
        
        if not self.recognizer or not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                logger.debug("Listening for voice command...")
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                try:
                    # Recognize speech using Google Web Speech API
                    text = self.recognizer.recognize_google(audio)
                    logger.info("Voice command recognized", text=text)
                    return text
                    
                except sr.UnknownValueError:
                    logger.debug("Could not understand voice command")
                    return None
                    
                except sr.RequestError as e:
                    logger.error("Voice recognition service error", error=str(e))
                    return None
                    
        except sr.WaitTimeoutError:
            logger.debug("Voice recognition timeout")
            return None
            
        except Exception as e:
            logger.error("Voice recognition error", error=str(e))
            return None
    
    def speak_response(self, text: str):
        """Speak response using TTS"""
        
        if not self.tts_engine:
            return
        
        try:
            logger.debug("Speaking response", text=text)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            logger.error("Text-to-speech error", error=str(e))
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Start continuous voice command listening"""
        
        if not self.recognizer or not self.microphone:
            logger.warning("Voice recognition not available")
            return
        
        self.is_listening = True
        
        def listen_loop():
            while self.is_listening:
                try:
                    command = self.listen_for_command(timeout=1.0)
                    if command:
                        callback(command)
                        
                except Exception as e:
                    logger.error("Continuous listening error", error=str(e))
                    time.sleep(1.0)
        
        threading.Thread(target=listen_loop, daemon=True).start()
        logger.info("Started continuous voice listening")
    
    def stop_continuous_listening(self):
        """Stop continuous voice command listening"""
        self.is_listening = False
        logger.info("Stopped continuous voice listening")

class ResponseGenerator:
    """Generate natural language responses"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.context_aware = True
        
    def _load_response_templates(self) -> Dict[ResponseType, Dict[str, List[str]]]:
        """Load response templates"""
        return {
            ResponseType.ACKNOWLEDGMENT: {
                "default": [
                    "Understood.",
                    "Got it.",
                    "Roger that.",
                    "Will do.",
                    "On it."
                ],
                "combat": [
                    "Engaging in combat.",
                    "Starting attack sequence.",
                    "Combat initiated.",
                    "Weapons ready."
                ],
                "movement": [
                    "Moving to target location.",
                    "Navigation started.",
                    "Heading to destination.",
                    "Route calculated."
                ]
            },
            ResponseType.STATUS_REPORT: {
                "combat": [
                    "Combat status: {status}",
                    "Currently {action} with {health}% health",
                    "Combat active: {active}, Health: {health}%"
                ],
                "movement": [
                    "Current location: {location}",
                    "Moving to: {destination}",
                    "Position: {coordinates}"
                ],
                "system": [
                    "System status: {status}",
                    "All systems {status}",
                    "Current state: {state}"
                ]
            },
            ResponseType.ERROR: {
                "default": [
                    "I'm sorry, I didn't understand that.",
                    "Could you please rephrase that?",
                    "I'm not sure what you mean.",
                    "That command wasn't clear to me."
                ],
                "action_failed": [
                    "Unable to complete that action.",
                    "That action failed to execute.",
                    "Sorry, I couldn't do that."
                ]
            },
            ResponseType.WARNING: {
                "default": [
                    "Warning: {message}",
                    "Caution: {message}",
                    "Alert: {message}"
                ],
                "health": [
                    "Health is critically low!",
                    "Warning: Low health detected!",
                    "Health critical - seek healing!"
                ]
            },
            ResponseType.QUESTION: {
                "confirmation": [
                    "Are you sure you want to {action}?",
                    "Confirm: {action}?",
                    "Should I proceed with {action}?"
                ],
                "clarification": [
                    "Did you mean {option1} or {option2}?",
                    "Which {item} did you want?",
                    "Can you be more specific about {topic}?"
                ]
            },
            ResponseType.SUCCESS: {
                "default": [
                    "Task completed successfully.",
                    "Done!",
                    "Success!",
                    "Completed."
                ],
                "combat": [
                    "Combat completed successfully.",
                    "Enemy defeated!",
                    "Victory achieved!"
                ]
            }
        }
    
    def generate_response(self, 
                         response_type: ResponseType,
                         category: CommandCategory,
                         context: Dict[str, Any],
                         template_data: Dict[str, Any] = None) -> SystemResponse:
        """Generate appropriate response"""
        
        try:
            # Get templates for response type
            templates = self.response_templates.get(response_type, {})
            
            # Try category-specific templates first
            category_templates = templates.get(category.value)
            if not category_templates:
                category_templates = templates.get("default", ["I understand."])
            
            # Select template (could be made smarter with ML)
            import random
            template = random.choice(category_templates)
            
            # Format template with data
            if template_data:
                try:
                    text = template.format(**template_data)
                except KeyError:
                    text = template
            else:
                text = template
            
            # Determine if confirmation is needed
            requires_confirmation = self._requires_confirmation(response_type, context)
            
            # Generate actions to take
            actions = self._determine_actions(response_type, category, context)
            
            return SystemResponse(
                text=text,
                response_type=response_type,
                category=category,
                requires_confirmation=requires_confirmation,
                actions_to_take=actions,
                metadata=context
            )
            
        except Exception as e:
            logger.error("Response generation error", error=str(e))
            
            return SystemResponse(
                text="I'm having trouble processing that request.",
                response_type=ResponseType.ERROR,
                category=category
            )
    
    def _requires_confirmation(self, response_type: ResponseType, context: Dict[str, Any]) -> bool:
        """Determine if response requires user confirmation"""
        
        # High-risk actions require confirmation
        risky_actions = ["sell_all", "delete", "reset", "stop_all", "logout"]
        
        if context.get("action") in risky_actions:
            return True
        
        # Large value transactions
        if context.get("value", 0) > 1000:
            return True
        
        return False
    
    def _determine_actions(self, 
                          response_type: ResponseType,
                          category: CommandCategory,
                          context: Dict[str, Any]) -> List[str]:
        """Determine what actions to take based on response"""
        
        actions = []
        
        if response_type == ResponseType.ACKNOWLEDGMENT:
            action = context.get("action")
            if action:
                actions.append(f"execute_{action}")
        
        elif response_type == ResponseType.STATUS_REPORT:
            actions.append("gather_status_data")
            
        elif response_type == ResponseType.WARNING:
            actions.append("log_warning")
            actions.append("notify_user")
        
        return actions

class NaturalLanguageInterface:
    """Main natural language interface system"""
    
    def __init__(self, 
                 enable_voice: bool = True,
                 enable_advanced_nlp: bool = True,
                 conversation_timeout_minutes: int = 30):
        
        self.enable_voice = enable_voice
        self.enable_advanced_nlp = enable_advanced_nlp
        self.conversation_timeout_minutes = conversation_timeout_minutes
        
        # Core components
        self.pattern_matcher = CommandPatternMatcher()
        self.nlp_processor = NLPProcessor() if enable_advanced_nlp else None
        self.voice_interface = VoiceInterface() if enable_voice else None
        self.response_generator = ResponseGenerator()
        
        # Conversation management
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.global_context = ConversationContext(
            session_id="global",
            user_id="default",
            started_at=datetime.utcnow(),
            last_interaction=datetime.utcnow()
        )
        
        # Command processing
        self.command_callbacks: Dict[CommandCategory, List[Callable]] = defaultdict(list)
        self.response_callbacks: List[Callable[[SystemResponse], None]] = []
        
        # Background processing
        self.processing_active = False
        self.processing_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.interface_stats = {
            "commands_processed": 0,
            "voice_commands": 0,
            "text_commands": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "average_confidence": 0.0
        }
        
        # Observability
        self.observability_manager = get_observability_manager()
        
        logger.info("Natural language interface initialized",
                   voice_enabled=self.voice_interface is not None,
                   advanced_nlp=self.nlp_processor is not None)
    
    @trace_gaming_operation("process_natural_language")
    async def process_command(self, 
                            text: str,
                            user_id: str = "default",
                            session_id: Optional[str] = None) -> SystemResponse:
        """Process natural language command"""
        
        start_time = time.time()
        
        try:
            # Get or create conversation context
            context = self._get_conversation_context(user_id, session_id)
            context.last_interaction = datetime.utcnow()
            
            # Parse the command
            parsed_command = await self._parse_command(text, context)
            
            if not parsed_command:
                self.interface_stats["failed_parses"] += 1
                return self.response_generator.generate_response(
                    ResponseType.ERROR,
                    CommandCategory.SYSTEM,
                    {"error": "parse_failed"}
                )
            
            # Update statistics
            self.interface_stats["commands_processed"] += 1
            self.interface_stats["successful_parses"] += 1
            
            # Update rolling average confidence
            current_avg = self.interface_stats["average_confidence"]
            total_commands = self.interface_stats["successful_parses"]
            new_avg = ((current_avg * (total_commands - 1)) + parsed_command.confidence) / total_commands
            self.interface_stats["average_confidence"] = new_avg
            
            # Add to conversation history
            context.command_history.append(parsed_command)
            
            # Handle confirmation flows
            if context.conversation_state == "waiting_confirmation":
                return await self._handle_confirmation(parsed_command, context)
            
            # Generate response
            response = await self._generate_command_response(parsed_command, context)
            
            # Execute callbacks
            await self._execute_command_callbacks(parsed_command, response)
            
            # Log processing time
            processing_time = time.time() - start_time
            logger.debug("Command processed",
                        command=text,
                        intent=parsed_command.intent.value,
                        category=parsed_command.category.value,
                        confidence=parsed_command.confidence,
                        processing_time=processing_time)
            
            return response
            
        except Exception as e:
            logger.error("Command processing error", command=text, error=str(e))
            
            return SystemResponse(
                text="I encountered an error processing that command.",
                response_type=ResponseType.ERROR,
                category=CommandCategory.SYSTEM,
                metadata={"error": str(e)}
            )
    
    async def _parse_command(self, text: str, context: ConversationContext) -> Optional[ParsedCommand]:
        """Parse natural language command"""
        
        try:
            # Pattern matching
            pattern_result = self.pattern_matcher.match_command(text)
            
            if not pattern_result:
                return None
            
            category, intent, action, pattern_confidence = pattern_result
            
            # Extract entities
            entities = self.pattern_matcher.extract_entities(text)
            
            # Advanced NLP processing if available
            if self.nlp_processor and self.nlp_processor.is_initialized:
                # Intent analysis
                nlp_intent, nlp_confidence = self.nlp_processor.analyze_intent(text)
                
                # Named entity extraction
                named_entities = self.nlp_processor.extract_named_entities(text)
                
                # Sentiment analysis
                sentiment, sentiment_confidence = self.nlp_processor.analyze_sentiment(text)
                
                # Combine confidences (weighted average)
                final_confidence = (pattern_confidence * 0.6) + (nlp_confidence * 0.4)
                
                # Use NLP intent if high confidence
                if nlp_confidence > 0.8:
                    intent = nlp_intent
                
                # Merge entities
                for entity_type, entity_list in named_entities.items():
                    if entity_list:
                        entities[entity_type.lower()] = entity_list[0]
                
            else:
                final_confidence = pattern_confidence
            
            # Extract parameters from context and entities
            parameters = self._extract_parameters(text, entities, context)
            
            return ParsedCommand(
                original_text=text,
                cleaned_text=self.pattern_matcher._clean_text(text),
                intent=intent,
                category=category,
                action=action,
                parameters=parameters,
                entities=entities,
                confidence=final_confidence,
                confidence_level=ConfidenceLevel.MEDIUM,  # Set in __post_init__
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Command parsing error", text=text, error=str(e))
            return None
    
    def _extract_parameters(self, 
                           text: str, 
                           entities: Dict[str, str],
                           context: ConversationContext) -> Dict[str, Any]:
        """Extract command parameters"""
        
        parameters = {}
        
        # Copy entities as base parameters
        parameters.update(entities)
        
        # Add context-based parameters
        if context.user_preferences:
            parameters.update(context.user_preferences)
        
        # Extract specific parameter patterns
        text_lower = text.lower()
        
        # Duration parameters
        duration_patterns = [
            (r"for (\d+) minutes?", "duration_minutes"),
            (r"for (\d+) hours?", "duration_hours"),
            (r"for (\d+) seconds?", "duration_seconds")
        ]
        
        for pattern, param_name in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                parameters[param_name] = int(match.group(1))
        
        # Quantity parameters
        quantity_match = re.search(r"(\d+) (?:times?|x)", text_lower)
        if quantity_match:
            parameters["quantity"] = int(quantity_match.group(1))
        
        # Boolean parameters
        if "immediately" in text_lower or "now" in text_lower:
            parameters["immediate"] = True
        
        if "carefully" in text_lower or "safely" in text_lower:
            parameters["safe_mode"] = True
        
        return parameters
    
    async def _generate_command_response(self, 
                                       command: ParsedCommand,
                                       context: ConversationContext) -> SystemResponse:
        """Generate response to parsed command"""
        
        try:
            # Determine response type based on intent
            if command.intent == IntentType.STATUS_QUERY:
                response_type = ResponseType.STATUS_REPORT
                
            elif command.intent in [IntentType.START_ACTION, IntentType.STOP_ACTION]:
                if command.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]:
                    response_type = ResponseType.ACKNOWLEDGMENT
                else:
                    response_type = ResponseType.QUESTION
                    
            elif command.intent == IntentType.QUESTION:
                response_type = ResponseType.INFO
                
            elif command.intent == IntentType.CONFIGURATION:
                response_type = ResponseType.ACKNOWLEDGMENT
                
            else:
                response_type = ResponseType.ACKNOWLEDGMENT
            
            # Build template data
            template_data = {
                "action": command.action,
                "status": "active",  # Would come from actual system state
                "health": "85",      # Would come from actual character state
                **command.parameters
            }
            
            # Generate response
            response = self.response_generator.generate_response(
                response_type,
                command.category,
                {"command": command, "context": context},
                template_data
            )
            
            # Handle confirmation requirement
            if response.requires_confirmation:
                context.conversation_state = "waiting_confirmation"
                context.active_confirmations[command.action] = {
                    "command": command,
                    "timestamp": datetime.utcnow(),
                    "response": response
                }
            
            return response
            
        except Exception as e:
            logger.error("Response generation error", error=str(e))
            
            return SystemResponse(
                text="I'm having trouble generating a response.",
                response_type=ResponseType.ERROR,
                category=command.category
            )
    
    async def _handle_confirmation(self, 
                                 command: ParsedCommand,
                                 context: ConversationContext) -> SystemResponse:
        """Handle confirmation dialog"""
        
        try:
            # Check for confirmation or cancellation
            if command.intent == IntentType.CONFIRMATION:
                # Execute pending action
                pending_actions = list(context.active_confirmations.keys())
                if pending_actions:
                    action_key = pending_actions[0]
                    original_command = context.active_confirmations[action_key]["command"]
                    
                    # Clear confirmation state
                    context.conversation_state = "idle"
                    del context.active_confirmations[action_key]
                    
                    # Execute the original command
                    return await self._generate_command_response(original_command, context)
                
            elif command.intent == IntentType.CANCELLATION:
                # Cancel pending action
                context.conversation_state = "idle"
                context.active_confirmations.clear()
                
                return SystemResponse(
                    text="Action cancelled.",
                    response_type=ResponseType.ACKNOWLEDGMENT,
                    category=CommandCategory.SYSTEM
                )
            
            # Invalid response to confirmation
            return SystemResponse(
                text="Please confirm with 'yes' or cancel with 'no'.",
                response_type=ResponseType.QUESTION,
                category=CommandCategory.SYSTEM
            )
            
        except Exception as e:
            logger.error("Confirmation handling error", error=str(e))
            
            return SystemResponse(
                text="Error handling confirmation.",
                response_type=ResponseType.ERROR,
                category=CommandCategory.SYSTEM
            )
    
    async def _execute_command_callbacks(self, 
                                       command: ParsedCommand,
                                       response: SystemResponse):
        """Execute registered callbacks for command"""
        
        try:
            # Execute category-specific callbacks
            callbacks = self.command_callbacks.get(command.category, [])
            
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(command, response)
                    else:
                        callback(command, response)
                        
                except Exception as e:
                    logger.error("Command callback error", error=str(e))
            
            # Execute response callbacks
            for callback in self.response_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(response)
                    else:
                        callback(response)
                        
                except Exception as e:
                    logger.error("Response callback error", error=str(e))
                    
        except Exception as e:
            logger.error("Callback execution error", error=str(e))
    
    def _get_conversation_context(self, user_id: str, session_id: Optional[str]) -> ConversationContext:
        """Get or create conversation context"""
        
        if session_id:
            context_key = f"{user_id}_{session_id}"
        else:
            context_key = user_id
        
        if context_key not in self.active_conversations:
            self.active_conversations[context_key] = ConversationContext(
                session_id=session_id or "default",
                user_id=user_id,
                started_at=datetime.utcnow(),
                last_interaction=datetime.utcnow()
            )
        
        return self.active_conversations[context_key]
    
    def process_voice_command(self, timeout: float = 5.0) -> Optional[SystemResponse]:
        """Process single voice command"""
        
        if not self.voice_interface:
            return None
        
        try:
            # Listen for command
            voice_text = self.voice_interface.listen_for_command(timeout)
            
            if voice_text:
                self.interface_stats["voice_commands"] += 1
                
                # Process as normal command
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                response = loop.run_until_complete(self.process_command(voice_text))
                
                # Speak the response
                self.voice_interface.speak_response(response.text)
                
                loop.close()
                
                return response
            
        except Exception as e:
            logger.error("Voice command processing error", error=str(e))
        
        return None
    
    def start_voice_listening(self):
        """Start continuous voice command listening"""
        
        if not self.voice_interface:
            logger.warning("Voice interface not available")
            return
        
        def voice_callback(command_text: str):
            try:
                self.interface_stats["voice_commands"] += 1
                
                # Process command asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                response = loop.run_until_complete(self.process_command(command_text))
                
                # Speak response
                self.voice_interface.speak_response(response.text)
                
                loop.close()
                
            except Exception as e:
                logger.error("Voice callback error", error=str(e))
        
        self.voice_interface.start_continuous_listening(voice_callback)
        logger.info("Started continuous voice command listening")
    
    def stop_voice_listening(self):
        """Stop continuous voice command listening"""
        if self.voice_interface:
            self.voice_interface.stop_continuous_listening()
    
    def add_command_callback(self, category: CommandCategory, callback: Callable):
        """Add callback for specific command category"""
        self.command_callbacks[category].append(callback)
    
    def add_response_callback(self, callback: Callable[[SystemResponse], None]):
        """Add callback for all responses"""
        self.response_callbacks.append(callback)
    
    def get_interface_stats(self) -> Dict[str, Any]:
        """Get interface performance statistics"""
        stats = self.interface_stats.copy()
        
        # Add derived metrics
        if stats["commands_processed"] > 0:
            stats["success_rate"] = stats["successful_parses"] / stats["commands_processed"]
            stats["voice_command_percentage"] = stats["voice_commands"] / stats["commands_processed"]
        else:
            stats["success_rate"] = 0.0
            stats["voice_command_percentage"] = 0.0
        
        stats["active_conversations"] = len(self.active_conversations)
        stats["voice_enabled"] = self.voice_interface is not None
        stats["advanced_nlp_enabled"] = self.nlp_processor is not None
        
        return stats
    
    def cleanup_expired_conversations(self):
        """Clean up expired conversation contexts"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=self.conversation_timeout_minutes)
            
            expired_contexts = [
                key for key, context in self.active_conversations.items()
                if context.last_interaction < cutoff_time
            ]
            
            for key in expired_contexts:
                del self.active_conversations[key]
            
            if expired_contexts:
                logger.info("Cleaned up expired conversations", count=len(expired_contexts))
                
        except Exception as e:
            logger.error("Conversation cleanup error", error=str(e))
    
    async def shutdown(self):
        """Shutdown natural language interface"""
        try:
            # Stop voice listening
            self.stop_voice_listening()
            
            # Clean up conversations
            self.active_conversations.clear()
            
            logger.info("Natural language interface shutdown completed")
            
        except Exception as e:
            logger.error("Failed to shutdown natural language interface", error=str(e))

# Global natural language interface instance
_global_nl_interface: Optional[NaturalLanguageInterface] = None

def initialize_natural_language_interface(**kwargs) -> NaturalLanguageInterface:
    """Initialize global natural language interface"""
    global _global_nl_interface
    
    _global_nl_interface = NaturalLanguageInterface(**kwargs)
    return _global_nl_interface

def get_natural_language_interface() -> Optional[NaturalLanguageInterface]:
    """Get global natural language interface instance"""
    return _global_nl_interface