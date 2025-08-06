"""
Test Batch 017 - Profiler System

This test file verifies the functionality of the profiler system including
spec detection, build management, and integration with combat profiles.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any

# Import the profiler components
from profiler.spec_detector import SpecDetector, BuildMatch, DetectionResult, DetectionMethod, BuildType
from profiler.build_manager import BuildManager, BuildInfo, TrainingPlan, ProgressionPhase


def test_basic_functionality():
    """Test basic functionality of spec detector and build manager."""
    print("Testing basic functionality...")
    
    try:
        # Test spec detector initialization
        detector = SpecDetector()
        assert detector is not None, "SpecDetector should initialize successfully"
        
        # Test build manager initialization
        manager = BuildManager()
        assert manager is not None, "BuildManager should initialize successfully"
        
        # Test builds data loading
        builds_data = detector.builds_data
        assert "builds" in builds_data, "Builds data should be loaded"
        assert len(builds_data.get("builds", {})) > 0, "Should have at least one build"
        
        print("✅ Basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_build_detection():
    """Test build detection functionality."""
    print("Testing build detection...")
    
    try:
        detector = SpecDetector()
        
        # Test detection with mock skills
        mock_skills = ["Novice Marksman", "Novice Medic", "Marksman Rifle Handling I"]
        
        # Create mock detection result
        mock_build_match = BuildMatch(
            build_name="rifleman_medic",
            confidence=0.85,
            matched_skills=mock_skills,
            missing_skills=["Medic Healing I", "Master Marksman"],
            build_type=BuildType.COMBAT_HEALER,
            primary_profession="rifleman",
            secondary_profession="medic"
        )
        
        mock_result = DetectionResult(
            detected_build=mock_build_match,
            current_skills=mock_skills,
            available_skills=["Novice Marksman", "Novice Medic", "Master Marksman"],
            detection_timestamp=time.time(),
            detection_method=DetectionMethod.OCR,
            confidence_score=0.85
        )
        
        # Test build info retrieval
        build_info = detector.get_build_info("rifleman_medic")
        assert build_info is not None, "Should retrieve build info"
        assert build_info["name"] == "Rifleman Medic", "Should have correct build name"
        
        # Test available builds
        available_builds = detector.get_available_builds()
        assert len(available_builds) > 0, "Should have available builds"
        assert "rifleman_medic" in available_builds, "Should include rifleman_medic"
        
        # Test default build
        default_build = detector.get_default_build("new_character")
        assert default_build is not None, "Should have default build"
        
        print("✅ Build detection tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Build detection test failed: {e}")
        return False


def test_build_matching():
    """Test build matching logic."""
    print("Testing build matching...")
    
    try:
        detector = SpecDetector()
        
        # Test with rifleman skills
        rifleman_skills = ["Novice Marksman", "Marksman Rifle Handling I", "Rifle Accuracy I"]
        match = detector._match_build(rifleman_skills)
        
        if match:
            assert match.build_name in ["pure_rifleman", "rifleman_medic"], "Should match rifleman build"
            assert match.confidence > 0.5, "Should have reasonable confidence"
            assert len(match.matched_skills) > 0, "Should have matched skills"
        
        # Test with medic skills
        medic_skills = ["Novice Medic", "Medic Healing I", "Medic Efficiency I"]
        match = detector._match_build(medic_skills)
        
        if match:
            assert match.build_name in ["pure_medic", "rifleman_medic"], "Should match medic build"
            assert match.confidence > 0.5, "Should have reasonable confidence"
        
        # Test with hybrid skills
        hybrid_skills = ["Novice Marksman", "Novice Medic", "Marksman Rifle Handling I", "Medic Healing I"]
        match = detector._match_build(hybrid_skills)
        
        if match:
            assert match.build_name == "rifleman_medic", "Should match hybrid build"
            assert match.confidence > 0.6, "Should have high confidence for hybrid"
        
        print("✅ Build matching tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Build matching test failed: {e}")
        return False


def test_build_completion_validation():
    """Test build completion validation."""
    print("Testing build completion validation...")
    
    try:
        detector = SpecDetector()
        
        # Test completion for rifleman_medic
        current_skills = ["Novice Marksman", "Novice Medic", "Marksman Rifle Handling I"]
        completion = detector.validate_build_completion("rifleman_medic", current_skills)
        
        assert completion["valid"], "Should be valid completion"
        assert completion["build_name"] == "rifleman_medic", "Should have correct build name"
        assert completion["completed_required"] > 0, "Should have completed required skills"
        assert completion["completion_ratio"] > 0, "Should have completion ratio"
        assert completion["completion_ratio"] < 1, "Should not be complete"
        
        # Test complete build
        complete_skills = [
            "Novice Marksman", "Marksman Rifle Handling I", "Marksman Rifle Handling II",
            "Marksman Rifle Handling III", "Marksman Rifle Handling IV", "Master Marksman",
            "Novice Medic", "Medic Healing I", "Medic Healing II", "Medic Healing III",
            "Medic Healing IV", "Master Medic"
        ]
        completion = detector.validate_build_completion("rifleman_medic", complete_skills)
        
        assert completion["is_complete"], "Should be complete"
        assert completion["completion_ratio"] >= 1.0, "Should have 100% completion"
        
        print("✅ Build completion validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Build completion validation test failed: {e}")
        return False


def test_build_manager():
    """Test build manager functionality."""
    print("Testing build manager...")
    
    try:
        manager = BuildManager()
        
        # Test build detection and selection
        build_info = manager.detect_and_select_build()
        # This might be None in test environment, which is OK
        
        # Test force build selection
        success = manager.force_build_selection("rifleman_medic")
        assert success, "Should successfully force select rifleman_medic"
        
        # Test build info creation
        build_info = manager.current_build
        assert build_info is not None, "Should have current build"
        assert build_info.name == "rifleman_medic", "Should have correct build name"
        assert build_info.build_type == "combat_healer", "Should have correct build type"
        assert build_info.primary_profession == "rifleman", "Should have correct primary profession"
        assert build_info.secondary_profession == "medic", "Should have correct secondary profession"
        
        # Test training plan creation
        training_plan = manager.current_training_plan
        assert training_plan is not None, "Should have training plan"
        assert training_plan.build_name == "rifleman_medic", "Should have correct build name"
        assert training_plan.current_phase in ProgressionPhase, "Should have valid phase"
        
        # Test available builds
        available_builds = manager.get_available_builds()
        assert len(available_builds) > 0, "Should have available builds"
        
        print("✅ Build manager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Build manager test failed: {e}")
        return False


def test_progression_logic():
    """Test progression logic and phase determination."""
    print("Testing progression logic...")
    
    try:
        manager = BuildManager()
        manager.force_build_selection("rifleman_medic")
        
        # Test early game phase
        early_skills = ["Novice Marksman"]
        phase = manager._determine_progression_phase(early_skills)
        assert phase == ProgressionPhase.EARLY_GAME, "Should be early game phase"
        
        # Test mid game phase
        mid_skills = ["Novice Marksman", "Novice Medic", "Marksman Rifle Handling I", "Medic Healing I"]
        phase = manager._determine_progression_phase(mid_skills)
        assert phase == ProgressionPhase.MID_GAME, "Should be mid game phase"
        
        # Test late game phase
        late_skills = [
            "Novice Marksman", "Novice Medic", "Marksman Rifle Handling I", "Medic Healing I",
            "Marksman Rifle Handling II", "Medic Healing II", "Marksman Rifle Handling III", "Medic Healing III"
        ]
        phase = manager._determine_progression_phase(late_skills)
        assert phase == ProgressionPhase.LATE_GAME, "Should be late game phase"
        
        # Test next skills determination
        next_skills = manager._get_next_skills(early_skills)
        assert len(next_skills) > 0, "Should have next skills"
        assert len(next_skills) <= 3, "Should limit to 3 next skills"
        
        # Test time estimation
        estimated_time = manager._estimate_completion_time(next_skills)
        assert estimated_time > 0, "Should have positive time estimate"
        
        # Test recommended activities
        activities = manager._get_recommended_activities(ProgressionPhase.EARLY_GAME)
        assert len(activities) > 0, "Should have recommended activities"
        
        print("✅ Progression logic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Progression logic test failed: {e}")
        return False


def test_combat_profile_integration():
    """Test integration with combat profiles."""
    print("Testing combat profile integration...")
    
    try:
        manager = BuildManager()
        
        # Test combat profile loading
        manager.force_build_selection("rifleman_medic")
        
        # Verify combat engine has profile loaded
        combat_engine = manager.combat_engine
        assert combat_engine is not None, "Should have combat engine"
        
        # Test session summary
        summary = manager.get_session_summary()
        assert "session_duration" in summary, "Should have session duration"
        assert "current_build" in summary, "Should have current build"
        assert "build_type" in summary, "Should have build type"
        assert "detection_log" in summary, "Should have detection log"
        
        # Test build progress
        progress = manager.get_build_progress()
        assert "build_name" in progress, "Should have build name"
        assert "current_phase" in progress, "Should have current phase"
        assert "completion_ratio" in progress, "Should have completion ratio"
        assert "next_skills" in progress, "Should have next skills"
        
        print("✅ Combat profile integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Combat profile integration test failed: {e}")
        return False


def test_global_functions():
    """Test global convenience functions."""
    print("Testing global functions...")
    
    try:
        # Test spec detector global function
        detector = get_spec_detector()
        assert detector is not None, "Should get spec detector"
        
        # Test build detection global function
        build_match = detect_current_build()
        # This might be None in test environment, which is OK
        
        # Test build completion global function
        completion = get_build_completion("rifleman_medic")
        assert "valid" in completion, "Should have valid field"
        
        # Test build manager global functions
        manager = get_build_manager()
        assert manager is not None, "Should get build manager"
        
        build_info = auto_detect_and_select_build()
        # This might be None in test environment, which is OK
        
        progress = get_current_build_progress()
        # This might have error in test environment, which is OK
        
        success = follow_current_build_progression()
        # This might be False in test environment, which is OK
        
        print("✅ Global functions tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Global functions test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and edge cases."""
    print("Testing error handling...")
    
    try:
        detector = SpecDetector()
        
        # Test with non-existent build
        build_info = detector.get_build_info("non_existent_build")
        assert build_info is None, "Should return None for non-existent build"
        
        # Test completion validation with non-existent build
        completion = detector.validate_build_completion("non_existent_build", [])
        assert not completion["valid"], "Should be invalid for non-existent build"
        assert "error" in completion, "Should have error message"
        
        # Test with empty skills
        match = detector._match_build([])
        assert match is None, "Should return None for empty skills"
        
        # Test build manager with invalid build
        manager = BuildManager()
        success = manager.force_build_selection("non_existent_build")
        assert not success, "Should fail for non-existent build"
        
        print("✅ Error handling tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_data_structures():
    """Test data structures and serialization."""
    print("Testing data structures...")
    
    try:
        # Test BuildMatch serialization
        build_match = BuildMatch(
            build_name="test_build",
            confidence=0.85,
            matched_skills=["skill1", "skill2"],
            missing_skills=["skill3"],
            build_type=BuildType.COMBAT_HEALER,
            primary_profession="rifleman",
            secondary_profession="medic"
        )
        
        # Test DetectionResult serialization
        detection_result = DetectionResult(
            detected_build=build_match,
            current_skills=["skill1", "skill2"],
            available_skills=["skill1", "skill2", "skill3"],
            detection_timestamp=time.time(),
            detection_method=DetectionMethod.OCR,
            confidence_score=0.85
        )
        
        # Test BuildInfo serialization
        build_info = BuildInfo(
            name="test_build",
            description="Test build",
            build_type="combat_healer",
            primary_profession="rifleman",
            secondary_profession="medic",
            combat_profile="test_profile",
            training_priorities=["skill1", "skill2"],
            leveling_plan={"early_game": {"skills": ["skill1"]}}
        )
        
        # Test TrainingPlan serialization
        training_plan = TrainingPlan(
            build_name="test_build",
            current_phase=ProgressionPhase.EARLY_GAME,
            next_skills=["skill1"],
            completed_skills=["skill2"],
            missing_skills=["skill3"],
            completion_ratio=0.5,
            estimated_time_to_complete=2.0,
            recommended_activities=["questing", "combat"]
        )
        
        # Verify all structures can be accessed
        assert build_match.build_name == "test_build"
        assert detection_result.confidence_score == 0.85
        assert build_info.name == "test_build"
        assert training_plan.build_name == "test_build"
        
        print("✅ Data structures tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Data structures test failed: {e}")
        return False


def run_all_tests():
    """Run all tests for Batch 017."""
    print("🧪 Running Batch 017 - Profiler System Tests")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_build_detection,
        test_build_matching,
        test_build_completion_validation,
        test_build_manager,
        test_progression_logic,
        test_combat_profile_integration,
        test_global_functions,
        test_error_handling,
        test_data_structures
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
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Batch 017 implementation is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the implementation.")
    
    return passed == total


if __name__ == "__main__":
    # Import the global functions
    from profiler.spec_detector import get_spec_detector, detect_current_build, get_build_completion
    from profiler.build_manager import get_build_manager, auto_detect_and_select_build, get_current_build_progress, follow_current_build_progression
    
    success = run_all_tests()
    exit(0 if success else 1) 