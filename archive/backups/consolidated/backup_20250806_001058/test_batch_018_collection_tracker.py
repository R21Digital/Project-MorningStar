"""
Test Batch 018 - Collection Tracker & Completion Path

This test file verifies the functionality of the enhanced collection tracker system
including zone-specific data, UI detection, goal triggering, and overlay functionality.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any

# Import the collection tracker components
from core.collection_tracker import (
    CollectionTracker, CollectionType, CollectionItem, CollectionStatus,
    get_collection_tracker, trigger_collection_goals, auto_complete_collections,
    get_collection_status, list_collections, detect_collected_items
)


def test_basic_functionality():
    """Test basic functionality of the enhanced collection tracker."""
    print("Testing basic functionality...")
    
    try:
        # Test tracker initialization
        tracker = CollectionTracker()
        assert tracker is not None, "CollectionTracker should initialize successfully"
        
        # Test collections loading
        assert len(tracker.collections) > 0, "Should have loaded collections"
        
        # Test zone-specific data loading
        zone_files = list(Path("data/collections").glob("*.json"))
        assert len(zone_files) > 0, "Should have zone-specific collection files"
        
        # Test progress tracking
        assert tracker.progress is not None, "Should have progress tracking"
        
        print("✅ Basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_zone_specific_data():
    """Test zone-specific collection data loading."""
    print("Testing zone-specific data...")
    
    try:
        tracker = CollectionTracker()
        
        # Check for zone-specific attributes
        zone_items = []
        for item in tracker.collections.values():
            if hasattr(item, 'subzone') and hasattr(item, 'ui_elements'):
                zone_items.append(item)
        
        assert len(zone_items) > 0, "Should have items with zone-specific data"
        
        # Test zone-specific attributes
        for item in zone_items:
            assert hasattr(item, 'subzone'), "Should have subzone attribute"
            assert hasattr(item, 'ui_elements'), "Should have ui_elements attribute"
            assert hasattr(item, 'ocr_patterns'), "Should have ocr_patterns attribute"
            assert hasattr(item, 'interaction_sequence'), "Should have interaction_sequence attribute"
            
            # Test UI elements structure
            if item.ui_elements:
                assert isinstance(item.ui_elements, dict), "UI elements should be a dict"
            
            # Test OCR patterns
            if item.ocr_patterns:
                assert isinstance(item.ocr_patterns, list), "OCR patterns should be a list"
                assert len(item.ocr_patterns) > 0, "Should have OCR patterns"
            
            # Test interaction sequence
            if item.interaction_sequence:
                assert isinstance(item.interaction_sequence, list), "Interaction sequence should be a list"
                assert len(item.interaction_sequence) > 0, "Should have interaction sequence"
        
        print("✅ Zone-specific data tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Zone-specific data test failed: {e}")
        return False


def test_enhanced_detection():
    """Test enhanced collection detection with OCR patterns."""
    print("Testing enhanced detection...")
    
    try:
        tracker = CollectionTracker()
        
        # Test detection with mock data
        mock_screen_text = "Trophy Collect Mos Eisley Cantina"
        detected_items = tracker.detect_collected_items()
        
        # Test detection methods
        detection_methods = ["trigger_text", "ocr_pattern", "type_keyword"]
        
        # Test with different collection types
        type_keywords = {
            CollectionType.TROPHY: ["trophy", "collect", "gather"],
            CollectionType.BADGE: ["badge", "earn", "receive"],
            CollectionType.LORE_ITEM: ["lore", "study", "examine"],
            CollectionType.ACHIEVEMENT: ["achievement", "complete"],
            CollectionType.DECORATION: ["decoration", "take", "decorative"]
        }
        
        for collection_type, keywords in type_keywords.items():
            items_of_type = [item for item in tracker.collections.values() 
                           if item.collection_type == collection_type]
            assert len(items_of_type) > 0, f"Should have {collection_type} items"
        
        print("✅ Enhanced detection tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced detection test failed: {e}")
        return False


def test_goal_triggering():
    """Test collection goal triggering functionality."""
    print("Testing goal triggering...")
    
    try:
        tracker = CollectionTracker()
        
        # Test goal triggering with mock location
        mock_location = (100, 100)
        goals = tracker.trigger_collection_goals(mock_location, max_distance=100)
        
        # Test priority calculation
        for item in tracker.collections.values():
            if item.coordinates:
                priority_score = tracker._calculate_priority_score(item, mock_location)
                assert priority_score >= 0, "Priority score should be non-negative"
                assert priority_score <= 5, "Priority score should be reasonable"
        
        # Test distance calculation
        for item in tracker.collections.values():
            if item.coordinates:
                distance = tracker._calculate_distance(mock_location, item.coordinates)
                assert distance >= 0, "Distance should be non-negative"
        
        # Test priority reasons
        for item in tracker.collections.values():
            reason = tracker._get_priority_reason(item)
            assert isinstance(reason, str), "Priority reason should be a string"
            assert len(reason) > 0, "Priority reason should not be empty"
        
        print("✅ Goal triggering tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Goal triggering test failed: {e}")
        return False


def test_priority_calculation():
    """Test priority calculation logic."""
    print("Testing priority calculation...")
    
    try:
        tracker = CollectionTracker()
        mock_location = (100, 100)
        
        # Test rarity priority
        rarity_scores = {
            "common": 1.0,
            "uncommon": 2.0,
            "rare": 3.0,
            "epic": 4.0,
            "legendary": 5.0
        }
        
        for rarity, expected_score in rarity_scores.items():
            # Create mock item with specific rarity
            mock_item = CollectionItem(
                name=f"Test {rarity}",
                collection_type=CollectionType.TROPHY,
                planet="Test",
                zone="Test",
                coordinates=(150, 150),
                rarity=rarity
            )
            
            score = tracker._calculate_priority_score(mock_item, mock_location)
            assert score > 0, f"Score should be positive for {rarity}"
        
        # Test type priority
        type_scores = {
            CollectionType.ACHIEVEMENT: 3.0,
            CollectionType.BADGE: 2.5,
            CollectionType.LORE_ITEM: 2.0,
            CollectionType.TROPHY: 1.5,
            CollectionType.DECORATION: 1.0
        }
        
        for collection_type, expected_score in type_scores.items():
            mock_item = CollectionItem(
                name=f"Test {collection_type.value}",
                collection_type=collection_type,
                planet="Test",
                zone="Test",
                coordinates=(150, 150),
                rarity="common"
            )
            
            score = tracker._calculate_priority_score(mock_item, mock_location)
            assert score > 0, f"Score should be positive for {collection_type}"
        
        print("✅ Priority calculation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Priority calculation test failed: {e}")
        return False


def test_auto_completion():
    """Test auto-completion functionality."""
    print("Testing auto-completion...")
    
    try:
        tracker = CollectionTracker()
        
        # Test auto-complete with mock location
        mock_location = (100, 100)
        success = tracker.auto_complete_collections(mock_location)
        
        # Success can be True or False depending on nearby items
        assert isinstance(success, bool), "Auto-complete should return boolean"
        
        # Test nearby item finding
        nearby_items = tracker.find_nearby_uncollected_items(mock_location, max_distance=100)
        assert isinstance(nearby_items, list), "Should return list of nearby items"
        
        # Test distance calculation
        for item in nearby_items:
            distance = tracker._calculate_distance(mock_location, item.coordinates)
            assert distance <= 100, "Nearby items should be within max distance"
        
        print("✅ Auto-completion tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Auto-completion test failed: {e}")
        return False


def test_logging_and_status():
    """Test logging and status reporting."""
    print("Testing logging and status...")
    
    try:
        tracker = CollectionTracker()
        
        # Test status reporting
        status = tracker.get_collection_status()
        assert isinstance(status, dict), "Status should be a dictionary"
        assert "total_collections" in status, "Should have total collections"
        assert "completed_collections" in status, "Should have completed collections"
        assert "progress_by_category" in status, "Should have progress by category"
        
        # Test progress tracking
        progress_data = status.get("progress_by_category", {})
        assert isinstance(progress_data, dict), "Progress data should be a dictionary"
        
        # Test collection listing
        all_collections = tracker.list_collections()
        assert isinstance(all_collections, list), "Should return list of collections"
        assert len(all_collections) > 0, "Should have collections"
        
        # Test filtered listing
        trophy_collections = tracker.list_collections(collection_type=CollectionType.TROPHY)
        assert isinstance(trophy_collections, list), "Should return filtered list"
        
        tatooine_collections = tracker.list_collections(planet="Tatooine")
        assert isinstance(tatooine_collections, list), "Should return filtered list"
        
        print("✅ Logging and status tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Logging and status test failed: {e}")
        return False


def test_global_functions():
    """Test global convenience functions."""
    print("Testing global functions...")
    
    try:
        # Test global tracker access
        tracker = get_collection_tracker()
        assert tracker is not None, "Should get collection tracker"
        
        # Test goal triggering
        goals = trigger_collection_goals((100, 100))
        assert isinstance(goals, list), "Should return list of goals"
        
        # Test auto-complete
        success = auto_complete_collections((100, 100))
        assert isinstance(success, bool), "Should return boolean"
        
        # Test status
        status = get_collection_status()
        assert isinstance(status, dict), "Should return status dictionary"
        
        # Test listing
        collections = list_collections()
        assert isinstance(collections, list), "Should return collections list"
        
        # Test detection
        detected = detect_collected_items()
        assert isinstance(detected, list), "Should return detected items list"
        
        print("✅ Global functions tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Global functions test failed: {e}")
        return False


def test_data_structures():
    """Test data structures and serialization."""
    print("Testing data structures...")
    
    try:
        # Test CollectionItem
        item = CollectionItem(
            name="Test Item",
            collection_type=CollectionType.TROPHY,
            planet="Test",
            zone="Test Zone",
            coordinates=(100, 200),
            trigger_text="Test Trigger",
            required_level=5,
            required_profession="test_profession",
            description="Test description",
            rarity="common"
        )
        
        # Test zone-specific attributes
        item.subzone = "Test Subzone"
        item.ui_elements = {"test": "value"}
        item.ocr_patterns = ["test", "pattern"]
        item.interaction_sequence = ["step1", "step2"]
        
        # Verify attributes
        assert item.name == "Test Item"
        assert item.collection_type == CollectionType.TROPHY
        assert item.coordinates == (100, 200)
        assert item.subzone == "Test Subzone"
        assert item.ui_elements == {"test": "value"}
        assert item.ocr_patterns == ["test", "pattern"]
        assert item.interaction_sequence == ["step1", "step2"]
        
        # Test enum values
        assert CollectionType.TROPHY.value == "trophy"
        assert CollectionType.BADGE.value == "badge"
        assert CollectionType.LORE_ITEM.value == "lore_item"
        assert CollectionType.ACHIEVEMENT.value == "achievement"
        assert CollectionType.DECORATION.value == "decoration"
        
        print("✅ Data structures tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Data structures test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and edge cases."""
    print("Testing error handling...")
    
    try:
        tracker = CollectionTracker()
        
        # Test with invalid coordinates
        invalid_location = (-1, -1)
        goals = tracker.trigger_collection_goals(invalid_location)
        assert isinstance(goals, list), "Should handle invalid coordinates gracefully"
        
        # Test with None location
        goals = tracker.trigger_collection_goals(None)
        assert isinstance(goals, list), "Should handle None location gracefully"
        
        # Test with empty collections
        original_collections = tracker.collections.copy()
        tracker.collections.clear()
        
        status = tracker.get_collection_status()
        assert status["total_collections"] == 0, "Should handle empty collections"
        
        # Restore collections
        tracker.collections = original_collections
        
        print("✅ Error handling tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_zone_files():
    """Test zone-specific collection files."""
    print("Testing zone files...")
    
    try:
        # Check zone files exist
        zone_dir = Path("data/collections")
        assert zone_dir.exists(), "Zone directory should exist"
        
        zone_files = list(zone_dir.glob("*.json"))
        assert len(zone_files) > 0, "Should have zone files"
        
        # Test file structure
        for zone_file in zone_files:
            with open(zone_file, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            assert "zone" in data, "Should have zone field"
            assert "collections" in data, "Should have collections array"
            assert "metadata" in data, "Should have metadata"
            
            # Check collections structure
            for collection in data["collections"]:
                assert "name" in collection, "Should have name"
                assert "type" in collection, "Should have type"
                assert "coordinates" in collection, "Should have coordinates"
                assert "ui_elements" in collection, "Should have ui_elements"
                assert "ocr_patterns" in collection, "Should have ocr_patterns"
                assert "interaction_sequence" in collection, "Should have interaction_sequence"
            
            # Check metadata structure
            metadata = data["metadata"]
            assert "total_collections" in metadata, "Should have total_collections"
            assert "categories" in metadata, "Should have categories"
            assert "subzones" in metadata, "Should have subzones"
            assert "rarity_distribution" in metadata, "Should have rarity_distribution"
        
        print("✅ Zone files tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Zone files test failed: {e}")
        return False


def run_all_tests():
    """Run all tests for Batch 018."""
    print("🧪 Running Batch 018 - Collection Tracker & Completion Path Tests")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_zone_specific_data,
        test_enhanced_detection,
        test_goal_triggering,
        test_priority_calculation,
        test_auto_completion,
        test_logging_and_status,
        test_global_functions,
        test_data_structures,
        test_error_handling,
        test_zone_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Batch 018 implementation is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 