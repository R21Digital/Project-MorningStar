# MS11 Batch 054 – Smart NPC Detection via Quest Giver Icons and OCR

## Overview

Batch 054 implements a comprehensive NPC detection system that uses computer vision to identify quest-giving NPCs through their distinctive yellow (!) and (?) icons. The system combines OpenCV template matching for icon detection with OCR for NPC name extraction, and cross-references detected NPCs with a quest sources database.

## Key Features

### 1. Quest Icon Detection
- **OpenCV Template Matching**: Uses template matching to detect yellow quest icons (!) and (?) in the game screen
- **Configurable Thresholds**: Adjustable confidence thresholds for icon detection (default: 0.7)
- **Duplicate Removal**: Intelligent removal of duplicate detections within close proximity
- **Multiple Search Regions**: Searches across different screen regions for optimal detection

### 2. NPC Name Extraction
- **OCR Integration**: Uses Tesseract OCR to extract NPC names from regions around detected icons
- **Text Cleaning**: Advanced text cleaning to remove OCR artifacts and common prefixes
- **Name Validation**: Comprehensive validation to ensure extracted text is a valid NPC name
- **Region Optimization**: Optimized regions around quest icons for better name extraction

### 3. Quest Sources Integration
- **Database Cross-Reference**: Cross-checks detected NPC names with `data/quest_sources.json`
- **Fuzzy Matching**: Supports both exact and partial name matching
- **Quest Information**: Retrieves detailed quest information including rewards, requirements, and locations
- **Planet/City Data**: Associates NPCs with their planet and city locations

### 4. CLI Debug Mode
- **Command-Line Interface**: Full CLI with various options for debugging and testing
- **Confidence Ratings**: Displays confidence scores for all detections
- **Detailed Output**: Shows available quests nearby with full details
- **Save Results**: Option to save detection results to JSON files

## Implementation Details

### Core Components

#### 1. `data/quest_sources.json`
```json
{
  "quest_sources": {
    "Janta Blood Collector": {
      "name": "Janta Blood Collector",
      "planet": "Tatooine",
      "city": "Mos Entha",
      "coordinates": {"x": 1234, "y": 5678},
      "quests": [
        {
          "id": "janta_blood_quest",
          "name": "Janta Blood Collection",
          "type": "gathering",
          "description": "Collect Janta Blood from local wildlife",
          "xp_reward": 500,
          "credit_reward": 200,
          "requirements": ["level_5", "scout_novice"]
        }
      ]
    }
  }
}
```

#### 2. `vision/npc_detector.py`

**Key Classes:**
- `QuestIcon`: Represents a detected quest icon with type, confidence, coordinates, and size
- `QuestNPC`: Represents a detected quest-giving NPC with name, icon, confidence, and quest data
- `QuestIconDetector`: Handles quest icon detection using OpenCV template matching
- `NPCDetector`: Main detector that combines icon detection and OCR

**Key Methods:**
- `detect_quest_icons(image)`: Detect quest icons in an image
- `detect_quest_npcs(image)`: Detect quest-giving NPCs with names and quest data
- `_extract_npc_name(image, icon)`: Extract NPC name using OCR
- `_find_quest_data(npc_name)`: Find quest data for an NPC name
- `get_available_quests_nearby()`: Get list of available quests with confidence ratings

**Global Convenience Functions:**
- `detect_quest_npcs(image)`: Global function to detect quest NPCs
- `get_available_quests_nearby()`: Global function to get available quests
- `set_debug_mode(enabled)`: Global function to set debug mode

#### 3. `cli/quest_detector.py`

**CLI Features:**
- `--debug`: Enable debug mode for detailed logging
- `--verbose`: Enable verbose output
- `--details`: Show detailed information about detected NPCs
- `--save FILE`: Save detection results to JSON file
- `--quests-only`: Show only available quests nearby
- `--confidence-threshold FLOAT`: Set minimum confidence threshold

### Integration Points

#### 1. Vision System Integration
The NPC detector integrates with the existing vision system:

```python
from vision.npc_detector import detect_quest_npcs, get_available_quests_nearby

# Detect quest NPCs in current screen
detected_npcs = detect_quest_npcs()

# Get available quests nearby
available_quests = get_available_quests_nearby()
```

#### 2. Quest System Integration
The detected NPCs can be integrated with the quest system:

```python
from vision.npc_detector import get_npc_detector

detector = get_npc_detector()
for npc in detected_npcs:
    if npc.quest_data:
        print(f"Found quest NPC: {npc.name}")
        print(f"Location: {npc.quest_data['city']}, {npc.quest_data['planet']}")
        for quest in npc.quest_data['quests']:
            print(f"  Quest: {quest['name']} ({quest['xp_reward']} XP)")
```

#### 3. Session Memory Integration
Detection results can be logged to session memory:

```python
from vision.npc_detector import detect_quest_npcs
from core.session_memory import MemoryManager

# Detect NPCs and log to session memory
detected_npcs = detect_quest_npcs()
memory_manager = MemoryManager()

for npc in detected_npcs:
    memory_manager.log_event(
        event_type="quest_npc_detected",
        data={
            "npc_name": npc.name,
            "icon_type": npc.icon_type,
            "confidence": npc.confidence,
            "quest_data": npc.quest_data
        }
    )
```

### Configuration Management

#### Detection Settings
- **confidence_threshold**: Minimum confidence for icon detection (default: 0.7)
- **min_icon_size**: Minimum icon size in pixels (default: 16x16)
- **max_icon_size**: Maximum icon size in pixels (default: 32x32)
- **npc_name_region_size**: Size of region to search for NPC names (default: 200x50)

#### OCR Settings
- **min_npc_name_length**: Minimum NPC name length (default: 3)
- **max_npc_name_length**: Maximum NPC name length (default: 50)
- **exclusion_patterns**: Patterns that indicate invalid NPC names

## Usage Examples

### Basic NPC Detection
```python
from vision.npc_detector import detect_quest_npcs

# Detect quest-giving NPCs in current screen
detected_npcs = detect_quest_npcs()

for npc in detected_npcs:
    print(f"Found NPC: {npc.name}")
    print(f"  Icon: {npc.icon_type} (confidence: {npc.confidence:.2f})")
    print(f"  Position: {npc.coordinates}")
    
    if npc.quest_data:
        print(f"  Planet: {npc.quest_data['planet']}")
        print(f"  City: {npc.quest_data['city']}")
```

### Available Quests Nearby
```python
from vision.npc_detector import get_available_quests_nearby

# Get available quests with confidence ratings
available_quests = get_available_quests_nearby()

for quest_info in available_quests:
    npc_name = quest_info['npc_name']
    confidence = quest_info['confidence']
    quests = quest_info['quests']
    
    print(f"{npc_name} (confidence: {confidence:.2f})")
    for quest in quests:
        print(f"  - {quest['name']}: {quest['xp_reward']} XP")
```

### CLI Usage
```bash
# Basic detection
python cli/quest_detector.py

# Debug mode with detailed output
python cli/quest_detector.py --debug --verbose

# Show only available quests
python cli/quest_detector.py --quests-only

# Save results to file
python cli/quest_detector.py --save results.json

# Custom confidence threshold
python cli/quest_detector.py --confidence-threshold 0.8
```

## Demo and Testing

### Demo Script: `demo_batch_054_npc_detector.py`
The demo showcases all major features:
- Quest icon detection with sample images
- NPC detection with simulated screen data
- Quest sources integration testing
- Available quests nearby functionality
- Debug mode testing
- Confidence threshold testing
- Error handling scenarios

### Test Suite: `test_batch_054_npc_detector.py`
Comprehensive test coverage including:
- **TestQuestIcon**: Quest icon dataclass tests
- **TestQuestNPC**: Quest NPC dataclass tests
- **TestQuestIconDetector**: Icon detection tests
- **TestNPCDetector**: Main detector tests
- **TestGlobalFunctions**: Global convenience function tests
- **TestIntegration**: End-to-end workflow tests
- **TestCLIIntegration**: CLI functionality tests

**Test Coverage:**
- ✅ QuestIcon creation and validation
- ✅ QuestNPC creation with and without quest data
- ✅ QuestIconDetector initialization and template creation
- ✅ Icon detection with mocked OpenCV functions
- ✅ Duplicate icon removal logic
- ✅ NPCDetector initialization and configuration
- ✅ Quest sources loading and error handling
- ✅ NPC name cleaning and validation
- ✅ Quest data finding with exact and partial matches
- ✅ NPC region calculation
- ✅ Debug mode functionality
- ✅ Global convenience functions
- ✅ Integration workflow testing
- ✅ Error handling scenarios
- ✅ CLI integration testing

## Performance Characteristics

### Detection Speed
- **Fast Icon Detection**: OpenCV template matching is highly optimized
- **Efficient OCR**: Tesseract OCR with optimized regions
- **Minimal Processing**: Only processes regions around detected icons
- **Caching**: Template images are cached for repeated use

### Accuracy
- **High Confidence Thresholds**: Default 0.7 threshold ensures high accuracy
- **Duplicate Removal**: Prevents false positives from multiple detections
- **Name Validation**: Comprehensive validation reduces OCR errors
- **Fuzzy Matching**: Handles OCR variations in NPC names

### Scalability
- **Configurable Regions**: Can adjust search regions for different screen sizes
- **Template Flexibility**: Easy to add new quest icon templates
- **Database Integration**: Scales with quest sources database size
- **Memory Efficient**: Minimal memory footprint for detection operations

## Future Enhancements

### 1. Advanced Icon Detection
- **Machine Learning**: Train custom models for better icon detection
- **Color-Based Detection**: Use color thresholds for more robust detection
- **Multi-Scale Detection**: Detect icons at different scales
- **Real-Time Detection**: Continuous monitoring for quest opportunities

### 2. Enhanced OCR
- **Custom OCR Models**: Train models specifically for game text
- **Multi-Language Support**: Support for different game languages
- **Text Preprocessing**: Advanced image preprocessing for better OCR
- **Confidence Scoring**: Better confidence scoring for OCR results

### 3. Quest System Integration
- **Automatic Quest Acceptance**: Automatically accept quests from detected NPCs
- **Quest Tracking**: Track accepted quests and their progress
- **Quest Optimization**: Suggest optimal quest paths based on detected NPCs
- **Quest History**: Maintain history of quest interactions

### 4. Advanced Features
- **NPC Movement Tracking**: Track NPC movement patterns
- **Quest Timing**: Detect quest availability timing
- **Multi-Player Integration**: Handle multiple players' quest states
- **Quest Chains**: Detect and manage quest chains and dependencies

## Error Handling

### Detection Errors
- **Template Loading**: Graceful handling of missing template files
- **OCR Failures**: Fallback mechanisms for OCR failures
- **Invalid Images**: Safe handling of corrupted or invalid images
- **Memory Errors**: Efficient memory management for large images

### Configuration Errors
- **Missing Quest Sources**: Graceful fallback when quest sources file is missing
- **Invalid JSON**: Clear error messages for corrupted configuration
- **Missing Fields**: Sensible defaults for missing configuration options

### Runtime Errors
- **Screen Capture Failures**: Handle screen capture errors gracefully
- **OpenCV Errors**: Proper error handling for OpenCV operations
- **File I/O Errors**: Robust handling of file operations

## Security Considerations

### Image Processing Security
- **Input Validation**: Validate all image inputs before processing
- **Memory Limits**: Set limits on image sizes to prevent memory issues
- **Path Validation**: Ensure all file paths are within expected directories

### Data Security
- **Quest Data Validation**: Validate all quest data before use
- **NPC Name Sanitization**: Sanitize NPC names to prevent injection attacks
- **Configuration Security**: Secure handling of configuration files

## Conclusion

Batch 054 successfully implements a comprehensive NPC detection system that provides:

1. **Accurate Icon Detection**: Reliable detection of quest icons using OpenCV
2. **Intelligent OCR**: Advanced OCR with text cleaning and validation
3. **Quest Integration**: Seamless integration with quest sources database
4. **CLI Interface**: Full command-line interface with debug capabilities
5. **Robust Testing**: Comprehensive test coverage for all functionality
6. **Future-Ready Design**: Extensible architecture for advanced features

The system integrates seamlessly with existing MS11 infrastructure and provides a solid foundation for advanced quest automation features in future batches.

## Files Created/Modified

### New Files
- `data/quest_sources.json`: Quest sources database with NPC and quest information
- `vision/npc_detector.py`: Main NPC detection system with icon detection and OCR
- `cli/quest_detector.py`: Command-line interface for NPC detection
- `demo_batch_054_npc_detector.py`: Comprehensive demo script
- `test_batch_054_npc_detector.py`: Complete test suite
- `BATCH_054_IMPLEMENTATION_SUMMARY.md`: This implementation summary

### Integration Points
- **Vision System**: Integrates with existing screen capture and OCR utilities
- **Quest System**: Provides foundation for automated quest detection and acceptance
- **Session Memory**: Can integrate with session tracking for quest events
- **CLI System**: Extends existing CLI infrastructure with new detection commands

The implementation provides a robust, tested, and extensible NPC detection system that enhances the MS11 bot's ability to automatically identify and interact with quest-giving NPCs, providing the foundation for advanced quest automation features. 