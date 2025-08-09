"""
MS11 Computer Vision Enhancement System
Advanced OCR, image recognition, and real-time screen analysis for improved game state detection
"""

import asyncio
import cv2
import numpy as np
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import json
import os
import base64
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from core.structured_logging import StructuredLogger
from core.observability_integration import get_observability_manager, trace_gaming_operation

# Initialize logger
logger = StructuredLogger("computer_vision")

class RecognitionConfidence(Enum):
    """OCR recognition confidence levels"""
    LOW = "low"          # 0-40%
    MEDIUM = "medium"    # 41-70%
    HIGH = "high"        # 71-85%
    VERY_HIGH = "very_high"  # 86-100%

class ImageType(Enum):
    """Types of game images to recognize"""
    UI_ELEMENT = "ui_element"
    CHAT_MESSAGE = "chat_message"
    QUEST_TEXT = "quest_text"
    INVENTORY_ITEM = "inventory_item"
    CHARACTER_STAT = "character_stat"
    MINIMAP = "minimap"
    HEALTH_BAR = "health_bar"
    EXPERIENCE_BAR = "experience_bar"
    GAME_MENU = "game_menu"
    DIALOG_BOX = "dialog_box"
    COMBAT_TEXT = "combat_text"

class TemplateMatchMethod(Enum):
    """OpenCV template matching methods"""
    CCOEFF = cv2.TM_CCOEFF
    CCOEFF_NORMED = cv2.TM_CCOEFF_NORMED
    CCORR = cv2.TM_CCORR
    CCORR_NORMED = cv2.TM_CCORR_NORMED
    SQDIFF = cv2.TM_SQDIFF
    SQDIFF_NORMED = cv2.TM_SQDIFF_NORMED

@dataclass
class OCRResult:
    """OCR recognition result"""
    text: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    confidence_level: RecognitionConfidence
    processing_time: float
    image_type: ImageType
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Set confidence level based on confidence score
        if self.confidence >= 86:
            self.confidence_level = RecognitionConfidence.VERY_HIGH
        elif self.confidence >= 71:
            self.confidence_level = RecognitionConfidence.HIGH
        elif self.confidence >= 41:
            self.confidence_level = RecognitionConfidence.MEDIUM
        else:
            self.confidence_level = RecognitionConfidence.LOW

@dataclass
class TemplateMatch:
    """Template matching result"""
    template_name: str
    location: Tuple[int, int]  # x, y coordinates of top-left corner
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    method_used: TemplateMatchMethod

@dataclass
class GameStateDetection:
    """Complete game state detection result"""
    timestamp: datetime
    screen_region: Tuple[int, int, int, int]
    ocr_results: List[OCRResult]
    template_matches: List[TemplateMatch]
    detected_ui_elements: List[str]
    game_state_confidence: float
    processing_time: float

class OCREngine:
    """Advanced OCR engine with multiple recognition strategies"""
    
    def __init__(self, 
                 tesseract_config: str = "--oem 3 --psm 6",
                 language: str = "eng",
                 confidence_threshold: float = 30.0):
        
        self.tesseract_config = tesseract_config
        self.language = language
        self.confidence_threshold = confidence_threshold
        
        # Image preprocessing configurations
        self.preprocessing_configs = {
            ImageType.CHAT_MESSAGE: {
                "resize_factor": 2.0,
                "blur_kernel": (1, 1),
                "threshold_type": cv2.THRESH_BINARY,
                "morphology": cv2.MORPH_CLOSE
            },
            ImageType.QUEST_TEXT: {
                "resize_factor": 1.5,
                "blur_kernel": (2, 2),
                "threshold_type": cv2.THRESH_BINARY_INV,
                "morphology": cv2.MORPH_OPEN
            },
            ImageType.CHARACTER_STAT: {
                "resize_factor": 3.0,
                "blur_kernel": (1, 1),
                "threshold_type": cv2.THRESH_BINARY,
                "morphology": None
            },
            ImageType.UI_ELEMENT: {
                "resize_factor": 2.0,
                "blur_kernel": (1, 1),
                "threshold_type": cv2.THRESH_BINARY,
                "morphology": cv2.MORPH_CLOSE
            }
        }
        
        # Text patterns for different game elements
        self.text_patterns = {
            ImageType.CHARACTER_STAT: r'\d+(?:/\d+)?',  # Numbers with optional slash
            ImageType.EXPERIENCE_BAR: r'(?:Level|Lvl)\s*\d+',
            ImageType.QUEST_TEXT: r'[A-Za-z\s]+(?:Quest|Task|Mission)',
            ImageType.CHAT_MESSAGE: r'^\[.*?\]\s*.*?:\s*.*$'
        }
        
    @trace_gaming_operation("ocr_text_recognition")
    def recognize_text(self, image: np.ndarray, image_type: ImageType = ImageType.UI_ELEMENT) -> OCRResult:
        """Perform OCR text recognition on image"""
        
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract not available, returning empty OCR result")
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_box=(0, 0, 0, 0),
                confidence_level=RecognitionConfidence.LOW,
                processing_time=0.0,
                image_type=image_type
            )
        
        start_time = time.time()
        
        try:
            # Preprocess image based on type
            processed_image = self._preprocess_image(image, image_type)
            
            # Perform OCR with confidence data
            ocr_data = pytesseract.image_to_data(
                processed_image,
                config=self.tesseract_config,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text and calculate confidence
            text_parts = []
            confidences = []
            boxes = []
            
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) > self.confidence_threshold:
                    text = ocr_data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(conf))
                        boxes.append((
                            ocr_data['left'][i],
                            ocr_data['top'][i],
                            ocr_data['width'][i],
                            ocr_data['height'][i]
                        ))
            
            # Combine results
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Calculate overall bounding box
            if boxes:
                min_x = min(box[0] for box in boxes)
                min_y = min(box[1] for box in boxes)
                max_x = max(box[0] + box[2] for box in boxes)
                max_y = max(box[1] + box[3] for box in boxes)
                overall_box = (min_x, min_y, max_x - min_x, max_y - min_y)
            else:
                overall_box = (0, 0, image.shape[1], image.shape[0])
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                bounding_box=overall_box,
                confidence_level=RecognitionConfidence.LOW,  # Will be set in __post_init__
                processing_time=processing_time,
                image_type=image_type,
                metadata={
                    "individual_confidences": confidences,
                    "word_count": len(text_parts),
                    "preprocessing_used": True
                }
            )
            
        except Exception as e:
            logger.error("OCR recognition error", error=str(e))
            processing_time = time.time() - start_time
            
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_box=(0, 0, 0, 0),
                confidence_level=RecognitionConfidence.LOW,
                processing_time=processing_time,
                image_type=image_type,
                metadata={"error": str(e)}
            )
    
    def _preprocess_image(self, image: np.ndarray, image_type: ImageType) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            config = self.preprocessing_configs.get(image_type, self.preprocessing_configs[ImageType.UI_ELEMENT])
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Resize for better recognition
            if config["resize_factor"] != 1.0:
                height, width = gray.shape
                new_height = int(height * config["resize_factor"])
                new_width = int(width * config["resize_factor"])
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Apply Gaussian blur to reduce noise
            if config["blur_kernel"] != (1, 1):
                gray = cv2.GaussianBlur(gray, config["blur_kernel"], 0)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, config["threshold_type"] + cv2.THRESH_OTSU)
            
            # Apply morphology operations if specified
            if config["morphology"]:
                kernel = np.ones((2, 2), np.uint8)
                thresh = cv2.morphologyEx(thresh, config["morphology"], kernel)
            
            return thresh
            
        except Exception as e:
            logger.error("Image preprocessing error", error=str(e))
            return image

class TemplateRecognizer:
    """Template matching for UI elements"""
    
    def __init__(self, templates_dir: str = "data/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, np.ndarray] = {}
        self.load_templates()
        
    def load_templates(self):
        """Load template images from directory"""
        try:
            if not self.templates_dir.exists():
                logger.warning("Templates directory does not exist", path=str(self.templates_dir))
                return
            
            for template_file in self.templates_dir.glob("*.png"):
                template_name = template_file.stem
                template_image = cv2.imread(str(template_file), 0)  # Load as grayscale
                
                if template_image is not None:
                    self.templates[template_name] = template_image
                    logger.debug("Loaded template", name=template_name, size=template_image.shape)
                else:
                    logger.warning("Failed to load template", path=str(template_file))
                    
        except Exception as e:
            logger.error("Error loading templates", error=str(e))
    
    @trace_gaming_operation("template_matching")
    def find_template(self, 
                     image: np.ndarray, 
                     template_name: str,
                     method: TemplateMatchMethod = TemplateMatchMethod.CCOEFF_NORMED,
                     threshold: float = 0.8) -> Optional[TemplateMatch]:
        """Find template in image using OpenCV template matching"""
        
        if template_name not in self.templates:
            logger.warning("Template not found", template_name=template_name)
            return None
        
        try:
            template = self.templates[template_name]
            
            # Convert image to grayscale if needed
            if len(image.shape) == 3:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = image
            
            # Perform template matching
            result = cv2.matchTemplate(gray_image, template, method.value)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # For SQDIFF methods, lower values are better matches
            if method in [TemplateMatchMethod.SQDIFF, TemplateMatchMethod.SQDIFF_NORMED]:
                match_val = min_val
                match_loc = min_loc
                confidence = 1.0 - match_val if method == TemplateMatchMethod.SQDIFF_NORMED else 1.0 / (1.0 + match_val)
            else:
                match_val = max_val
                match_loc = max_loc
                confidence = match_val
            
            # Check if match meets threshold
            if confidence >= threshold:
                template_h, template_w = template.shape
                
                return TemplateMatch(
                    template_name=template_name,
                    location=match_loc,
                    confidence=confidence,
                    bounding_box=(match_loc[0], match_loc[1], template_w, template_h),
                    method_used=method
                )
            
            return None
            
        except Exception as e:
            logger.error("Template matching error", template_name=template_name, error=str(e))
            return None
    
    def find_all_templates(self, 
                          image: np.ndarray, 
                          threshold: float = 0.8) -> List[TemplateMatch]:
        """Find all loaded templates in image"""
        matches = []
        
        for template_name in self.templates:
            match = self.find_template(image, template_name, threshold=threshold)
            if match:
                matches.append(match)
        
        return matches

class ScreenCapture:
    """Real-time screen capture and region monitoring"""
    
    def __init__(self, monitor_region: Optional[Tuple[int, int, int, int]] = None):
        self.monitor_region = monitor_region  # x, y, width, height
        self.screenshot_cache = {}
        self.cache_duration = 0.5  # Cache screenshots for 500ms
        
        # Initialize MSS for fast screenshots
        if MSS_AVAILABLE:
            self.sct = mss.mss()
        else:
            self.sct = None
            logger.warning("MSS not available, screen capture will be slower")
    
    @trace_gaming_operation("screen_capture")
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen or screen region"""
        
        capture_region = region or self.monitor_region
        
        try:
            if self.sct and capture_region:
                # Use MSS for fast capture
                monitor = {
                    "top": capture_region[1],
                    "left": capture_region[0],
                    "width": capture_region[2],
                    "height": capture_region[3]
                }
                
                screenshot = self.sct.grab(monitor)
                img_array = np.array(screenshot)
                
                # Convert BGRA to BGR
                if img_array.shape[2] == 4:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
                
                return img_array
                
            else:
                # Fallback to PIL/other methods
                if PIL_AVAILABLE:
                    screenshot = ImageGrab.grab(capture_region)
                    return np.array(screenshot)
                else:
                    logger.error("No screen capture method available")
                    return np.zeros((100, 100, 3), dtype=np.uint8)
                    
        except Exception as e:
            logger.error("Screen capture error", error=str(e))
            return np.zeros((100, 100, 3), dtype=np.uint8)
    
    def capture_with_cache(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen with caching to avoid excessive captures"""
        
        cache_key = str(region or self.monitor_region)
        current_time = time.time()
        
        # Check cache
        if cache_key in self.screenshot_cache:
            cached_screenshot, cached_time = self.screenshot_cache[cache_key]
            if current_time - cached_time < self.cache_duration:
                return cached_screenshot
        
        # Capture new screenshot
        screenshot = self.capture_screen(region)
        self.screenshot_cache[cache_key] = (screenshot, current_time)
        
        return screenshot

class ComputerVisionManager:
    """Main computer vision manager coordinating OCR, template matching, and screen capture"""
    
    def __init__(self,
                 templates_dir: str = "data/templates",
                 monitor_region: Optional[Tuple[int, int, int, int]] = None,
                 ocr_confidence_threshold: float = 50.0):
        
        # Initialize components
        self.ocr_engine = OCREngine(confidence_threshold=ocr_confidence_threshold)
        self.template_recognizer = TemplateRecognizer(templates_dir)
        self.screen_capture = ScreenCapture(monitor_region)
        
        # Game state detection
        self.ui_element_detectors = {
            "health_bar": self._detect_health_bar,
            "experience_bar": self._detect_experience_bar,
            "chat_window": self._detect_chat_window,
            "inventory": self._detect_inventory,
            "quest_log": self._detect_quest_log,
            "minimap": self._detect_minimap
        }
        
        # Performance tracking
        self.performance_stats = {
            "total_detections": 0,
            "successful_detections": 0,
            "avg_processing_time": 0.0,
            "last_detection_time": None
        }
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.detection_callbacks: List[Callable[[GameStateDetection], None]] = []
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Observability
        self.observability_manager = get_observability_manager()
    
    @trace_gaming_operation("game_state_detection")
    async def detect_game_state(self, 
                               screen_region: Optional[Tuple[int, int, int, int]] = None,
                               detect_ui_elements: bool = True,
                               perform_ocr: bool = True) -> GameStateDetection:
        """Perform comprehensive game state detection"""
        
        start_time = time.time()
        detection_timestamp = datetime.utcnow()
        
        try:
            # Capture screen
            screenshot = self.screen_capture.capture_with_cache(screen_region)
            
            # Initialize result containers
            ocr_results = []
            template_matches = []
            detected_ui_elements = []
            
            # Perform parallel processing
            tasks = []
            
            # OCR recognition task
            if perform_ocr:
                ocr_task = asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    self._perform_ocr_analysis,
                    screenshot
                )
                tasks.append(("ocr", ocr_task))
            
            # Template matching task
            template_task = asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self._perform_template_matching,
                screenshot
            )
            tasks.append(("template", template_task))
            
            # UI element detection task
            if detect_ui_elements:
                ui_task = asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    self._detect_ui_elements,
                    screenshot
                )
                tasks.append(("ui", ui_task))
            
            # Wait for all tasks to complete
            for task_name, task in tasks:
                try:
                    result = await task
                    
                    if task_name == "ocr":
                        ocr_results = result
                    elif task_name == "template":
                        template_matches = result
                    elif task_name == "ui":
                        detected_ui_elements = result
                        
                except Exception as e:
                    logger.error(f"{task_name} task failed", error=str(e))
            
            # Calculate overall confidence
            game_state_confidence = self._calculate_game_state_confidence(
                ocr_results, template_matches, detected_ui_elements
            )
            
            processing_time = time.time() - start_time
            
            # Update performance stats
            self._update_performance_stats(processing_time, game_state_confidence > 0.5)
            
            result = GameStateDetection(
                timestamp=detection_timestamp,
                screen_region=screen_region or (0, 0, screenshot.shape[1], screenshot.shape[0]),
                ocr_results=ocr_results,
                template_matches=template_matches,
                detected_ui_elements=detected_ui_elements,
                game_state_confidence=game_state_confidence,
                processing_time=processing_time
            )
            
            # Notify callbacks
            for callback in self.detection_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    logger.error("Detection callback error", error=str(e))
            
            return result
            
        except Exception as e:
            logger.error("Game state detection error", error=str(e))
            processing_time = time.time() - start_time
            
            return GameStateDetection(
                timestamp=detection_timestamp,
                screen_region=screen_region or (0, 0, 0, 0),
                ocr_results=[],
                template_matches=[],
                detected_ui_elements=[],
                game_state_confidence=0.0,
                processing_time=processing_time
            )
    
    def _perform_ocr_analysis(self, screenshot: np.ndarray) -> List[OCRResult]:
        """Perform OCR analysis on different regions of the screen"""
        ocr_results = []
        
        try:
            # Define regions for different types of text
            height, width = screenshot.shape[:2]
            regions = {
                ImageType.CHAT_MESSAGE: (0, int(height * 0.6), width, int(height * 0.4)),  # Bottom 40%
                ImageType.QUEST_TEXT: (int(width * 0.7), 0, int(width * 0.3), int(height * 0.3)),  # Top-right
                ImageType.CHARACTER_STAT: (0, 0, int(width * 0.3), int(height * 0.3)),  # Top-left
                ImageType.UI_ELEMENT: (0, 0, width, height)  # Full screen
            }
            
            for image_type, (x, y, w, h) in regions.items():
                region = screenshot[y:y+h, x:x+w]
                
                if region.size > 0:
                    result = self.ocr_engine.recognize_text(region, image_type)
                    if result.text.strip():
                        # Adjust bounding box to screen coordinates
                        bbox = result.bounding_box
                        adjusted_bbox = (bbox[0] + x, bbox[1] + y, bbox[2], bbox[3])
                        result.bounding_box = adjusted_bbox
                        ocr_results.append(result)
            
        except Exception as e:
            logger.error("OCR analysis error", error=str(e))
        
        return ocr_results
    
    def _perform_template_matching(self, screenshot: np.ndarray) -> List[TemplateMatch]:
        """Perform template matching on screenshot"""
        try:
            return self.template_recognizer.find_all_templates(screenshot, threshold=0.7)
        except Exception as e:
            logger.error("Template matching error", error=str(e))
            return []
    
    def _detect_ui_elements(self, screenshot: np.ndarray) -> List[str]:
        """Detect UI elements using various methods"""
        detected_elements = []
        
        try:
            for element_name, detector_func in self.ui_element_detectors.items():
                try:
                    if detector_func(screenshot):
                        detected_elements.append(element_name)
                except Exception as e:
                    logger.error(f"UI element detection error for {element_name}", error=str(e))
                    
        except Exception as e:
            logger.error("UI element detection error", error=str(e))
        
        return detected_elements
    
    # UI element detection methods
    def _detect_health_bar(self, screenshot: np.ndarray) -> bool:
        """Detect health bar presence"""
        # Simple color-based detection for red health bars
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Define range for red color (health bar)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # Check if there's a significant horizontal red region (health bar)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3))
        red_horizontal = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, horizontal_kernel)
        
        return np.sum(red_horizontal) > 1000
    
    def _detect_experience_bar(self, screenshot: np.ndarray) -> bool:
        """Detect experience bar presence"""
        # Look for blue/yellow horizontal bars (common XP bar colors)
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Blue range
        lower_blue = np.array([100, 120, 70])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Yellow range
        lower_yellow = np.array([20, 120, 70])
        upper_yellow = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        combined_mask = blue_mask + yellow_mask
        
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 2))
        horizontal_bars = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, horizontal_kernel)
        
        return np.sum(horizontal_bars) > 500
    
    def _detect_chat_window(self, screenshot: np.ndarray) -> bool:
        """Detect chat window presence"""
        # Look for text regions in the bottom portion of screen
        height = screenshot.shape[0]
        chat_region = screenshot[int(height * 0.6):, :]
        
        # Convert to grayscale and look for text-like patterns
        gray = cv2.cvtColor(chat_region, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for horizontal text lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, horizontal_kernel)
        
        # Count horizontal line segments (potential text lines)
        contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        text_lines = len([c for c in contours if cv2.contourArea(c) > 50])
        
        return text_lines >= 3
    
    def _detect_inventory(self, screenshot: np.ndarray) -> bool:
        """Detect inventory window presence"""
        # Look for grid-like patterns typical of inventory
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for rectangular grid patterns
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangular_contours = 0
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4 and cv2.contourArea(contour) > 100:
                rectangular_contours += 1
        
        return rectangular_contours >= 8  # Inventory typically has multiple slots
    
    def _detect_quest_log(self, screenshot: np.ndarray) -> bool:
        """Detect quest log presence"""
        # Look for structured text layout in quest log area
        height, width = screenshot.shape[:2]
        quest_region = screenshot[:int(height * 0.6), int(width * 0.6):]
        
        gray = cv2.cvtColor(quest_region, cv2.COLOR_BGR2GRAY)
        
        # Look for text structure typical of quest logs
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find text regions
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
        text_regions = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, horizontal_kernel)
        
        contours, _ = cv2.findContours(text_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        text_lines = len([c for c in contours if cv2.contourArea(c) > 100])
        
        return text_lines >= 2
    
    def _detect_minimap(self, screenshot: np.ndarray) -> bool:
        """Detect minimap presence"""
        # Look for circular or square regions typically in corners
        height, width = screenshot.shape[:2]
        
        # Check corners for minimap
        corner_regions = [
            screenshot[:int(height * 0.3), :int(width * 0.3)],     # Top-left
            screenshot[:int(height * 0.3), -int(width * 0.3):],    # Top-right
            screenshot[-int(height * 0.3):, :int(width * 0.3)],    # Bottom-left
            screenshot[-int(height * 0.3):, -int(width * 0.3):]    # Bottom-right
        ]
        
        for region in corner_regions:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30, minRadius=30, maxRadius=100
            )
            
            if circles is not None and len(circles[0]) > 0:
                return True
        
        return False
    
    def _calculate_game_state_confidence(self, 
                                       ocr_results: List[OCRResult],
                                       template_matches: List[TemplateMatch],
                                       detected_ui_elements: List[str]) -> float:
        """Calculate overall confidence in game state detection"""
        
        confidence_factors = []
        
        # OCR confidence
        if ocr_results:
            avg_ocr_confidence = sum(r.confidence for r in ocr_results) / len(ocr_results)
            confidence_factors.append(avg_ocr_confidence / 100.0)
        
        # Template matching confidence
        if template_matches:
            avg_template_confidence = sum(m.confidence for m in template_matches) / len(template_matches)
            confidence_factors.append(avg_template_confidence)
        
        # UI elements detection
        ui_confidence = min(len(detected_ui_elements) / 6.0, 1.0)  # Max 6 UI elements
        confidence_factors.append(ui_confidence)
        
        # Calculate weighted average
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.0
    
    def _update_performance_stats(self, processing_time: float, success: bool):
        """Update performance statistics"""
        self.performance_stats["total_detections"] += 1
        
        if success:
            self.performance_stats["successful_detections"] += 1
        
        # Update average processing time
        current_avg = self.performance_stats["avg_processing_time"]
        total = self.performance_stats["total_detections"]
        
        self.performance_stats["avg_processing_time"] = (
            (current_avg * (total - 1)) + processing_time
        ) / total
        
        self.performance_stats["last_detection_time"] = datetime.utcnow()
    
    def add_detection_callback(self, callback: Callable[[GameStateDetection], None]):
        """Add callback for detection results"""
        self.detection_callbacks.append(callback)
    
    def start_continuous_monitoring(self, interval: float = 1.0):
        """Start continuous background monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("Started continuous monitoring", interval=interval)
    
    def stop_continuous_monitoring(self):
        """Stop continuous background monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        logger.info("Stopped continuous monitoring")
    
    def _monitoring_loop(self, interval: float):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Run detection in event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                detection = loop.run_until_complete(self.detect_game_state())
                
                # Log detection results
                logger.debug("Background detection completed",
                           confidence=detection.game_state_confidence,
                           ocr_count=len(detection.ocr_results),
                           template_count=len(detection.template_matches),
                           ui_count=len(detection.detected_ui_elements))
                
                loop.close()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error("Monitoring loop error", error=str(e))
                time.sleep(interval)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.performance_stats.copy()
        
        if stats["total_detections"] > 0:
            stats["success_rate"] = stats["successful_detections"] / stats["total_detections"]
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def export_detection_data(self, detection: GameStateDetection, output_dir: str = "data/detections"):
        """Export detection data for analysis"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp_str = detection.timestamp.strftime("%Y%m%d_%H%M%S_%f")
            filename = f"detection_{timestamp_str}.json"
            
            # Prepare data for JSON serialization
            detection_data = {
                "timestamp": detection.timestamp.isoformat(),
                "screen_region": detection.screen_region,
                "ocr_results": [asdict(ocr) for ocr in detection.ocr_results],
                "template_matches": [asdict(match) for match in detection.template_matches],
                "detected_ui_elements": detection.detected_ui_elements,
                "game_state_confidence": detection.game_state_confidence,
                "processing_time": detection.processing_time
            }
            
            with open(output_path / filename, 'w') as f:
                json.dump(detection_data, f, indent=2, default=str)
            
            logger.info("Exported detection data", filename=filename)
            
        except Exception as e:
            logger.error("Failed to export detection data", error=str(e))
    
    async def shutdown(self):
        """Shutdown computer vision manager"""
        try:
            # Stop monitoring
            self.stop_continuous_monitoring()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("Computer vision manager shutdown completed")
            
        except Exception as e:
            logger.error("Failed to shutdown computer vision manager", error=str(e))

# Global computer vision manager instance
_global_cv_manager: Optional[ComputerVisionManager] = None

def initialize_computer_vision(**kwargs) -> ComputerVisionManager:
    """Initialize global computer vision manager"""
    global _global_cv_manager
    
    _global_cv_manager = ComputerVisionManager(**kwargs)
    return _global_cv_manager

def get_computer_vision_manager() -> Optional[ComputerVisionManager]:
    """Get global computer vision manager instance"""
    return _global_cv_manager