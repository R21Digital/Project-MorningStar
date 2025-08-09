#!/usr/bin/env python3
"""
MS11 AI Integration Test
Test the new AI modules in isolation to verify functionality
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_behavioral_learning():
    """Test behavioral learning module"""
    print("Testing Behavioral Learning Module...")
    
    try:
        # Test basic imports
        from ai.behavioral_learning import (
            BehaviorEvent, BehaviorType, BehaviorLearningManager, 
            initialize_behavioral_learning
        )
        
        # Test initialization
        manager = initialize_behavioral_learning(
            data_retention_days=7,
            analysis_interval_hours=1,
            enable_predictions=True,
            enable_adaptations=True
        )
        
        # Test event recording
        event = BehaviorEvent(
            timestamp=datetime.utcnow(),
            behavior_type=BehaviorType.COMBAT_PATTERN,
            action="attack_mob",
            context={"target": "test_mob", "location": "tatooine"},
            outcome="success",
            success=True,
            duration=30.0
        )
        
        manager.record_behavior_event(event)
        
        # Test stats
        stats = manager.get_learning_stats()
        print(f"  [OK] Behavioral learning stats: {stats}")
        
        print("  [OK] Behavioral Learning Module - PASSED")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Behavioral Learning Module failed: {str(e)}")
        return False

def test_computer_vision():
    """Test computer vision module"""
    print("Testing Computer Vision Module...")
    
    try:
        # Test basic imports
        from ai.computer_vision import (
            ComputerVisionManager, OCREngine, TemplateRecognizer,
            ImageType, initialize_computer_vision
        )
        
        # Test initialization (without hardware dependencies)
        manager = initialize_computer_vision(
            templates_dir="data/templates",
            monitor_region=None,
            ocr_confidence_threshold=50.0
        )
        
        # Test performance stats
        stats = manager.get_performance_stats()
        print(f"  [OK] Computer vision stats: {stats}")
        
        print("  [OK] Computer Vision Module - PASSED")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Computer Vision Module failed: {str(e)}")
        return False

def test_natural_language_interface():
    """Test natural language interface"""
    print("Testing Natural Language Interface...")
    
    try:
        # Test basic imports
        from ai.natural_language_interface import (
            NaturalLanguageInterface, CommandCategory, IntentType,
            initialize_natural_language_interface
        )
        
        # Test initialization (without hardware dependencies)
        interface = initialize_natural_language_interface(
            enable_voice=False,  # Disable voice for testing
            enable_advanced_nlp=False,  # Disable advanced NLP for testing
            conversation_timeout_minutes=30
        )
        
        # Test command processing
        async def test_command():
            response = await interface.process_command("show status")
            return response
        
        # Run async test
        response = asyncio.run(test_command())
        print(f"  [OK] Processed command: {response.text}")
        
        # Test stats
        stats = interface.get_interface_stats()
        print(f"  [OK] Natural language stats: {stats}")
        
        print("  [OK] Natural Language Interface - PASSED")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Natural Language Interface failed: {str(e)}")
        return False

def test_configuration_endpoints():
    """Test configuration API endpoints"""
    print("Testing Configuration API Endpoints...")
    
    try:
        # Test Flask app creation and endpoint registration
        from flask import Flask
        from api.rest_endpoints import api_bp
        
        app = Flask(__name__)
        app.register_blueprint(api_bp)
        
        # Test that endpoints are registered
        endpoints = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('api.'):
                endpoints.append(f"{rule.rule} ({rule.methods})")
        
        config_endpoints = [ep for ep in endpoints if 'config' in ep]
        print(f"  [OK] Configuration endpoints: {len(config_endpoints)} found")
        for endpoint in config_endpoints:
            print(f"    - {endpoint}")
        
        print("  [OK] Configuration API Endpoints - PASSED")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Configuration API Endpoints failed: {str(e)}")
        return False

def main():
    """Run all integration tests"""
    print("MS11 AI Integration Test Suite")
    print("=" * 40)
    
    tests = [
        test_behavioral_learning,
        test_computer_vision, 
        test_natural_language_interface,
        test_configuration_endpoints
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"Test {test_func.__name__} crashed: {str(e)}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("SUCCESS: All AI integration tests passed!")
        return 0
    else:
        print(f"WARNING: {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())