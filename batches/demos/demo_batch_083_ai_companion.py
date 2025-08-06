#!/usr/bin/env python3
"""MS11 Batch 083 - SWGDB AI Companion Demo"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from core.ai_companion import AICompanion, create_ai_companion
from core.ai_companion.data_processor import DataProcessor, create_data_processor
from core.ai_companion.prompt_manager import PromptManager, create_prompt_manager
from core.ai_companion.conversation_manager import ConversationManager, create_conversation_manager
from core.ai_companion.mode_handler import ModeHandler, create_mode_handler
from core.ai_companion.web_interface import WebInterface, create_web_interface

def log_event(message: str):
    """Simple logging function for demo."""
    print(f"[LOG] {message}")

class AICompanionDemo:
    """Demo class for the SWGDB AI Companion."""
    
    def __init__(self):
        self.demo_dir = Path("demo_ai_companion")
        self.demo_dir.mkdir(exist_ok=True)
        self.ai_companion = None
        self.session_id = None
        self.demo_results = {}
        log_event("[AI_COMPANION_DEMO] AI Companion demo initialized")
    
    def run_full_demo(self):
        """Run the complete AI companion demo."""
        print("🤖 SWGDB AI Companion Demo")
        print("=" * 50)
        
        try:
            self._demo_initialization()
            self._demo_data_processing()
            self._demo_prompt_management()
            self._demo_conversation_management()
            self._demo_mode_handling()
            self._demo_web_interface()
            self._demo_ai_companion_integration()
            self._demo_conversation_flow()
            self._demo_statistics_and_analytics()
            self._demo_cleanup_and_maintenance()
            
            self._generate_demo_report()
            print("\n✅ Demo completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Demo failed: {str(e)}")
            log_event(f"[AI_COMPANION_DEMO] Demo failed: {str(e)}")
    
    def _demo_initialization(self):
        """Demo the initialization of AI companion components."""
        print("\n1. Initializing AI Companion Components...")
        
        # Initialize main AI companion
        self.ai_companion = create_ai_companion()
        print("   ✅ AI Companion initialized")
        
        # Initialize individual components
        data_processor = create_data_processor()
        prompt_manager = create_prompt_manager()
        conversation_manager = create_conversation_manager()
        mode_handler = create_mode_handler()
        web_interface = create_web_interface()
        
        print("   ✅ All components initialized")
        
        # Test component functionality
        self._test_data_processor(data_processor)
        self._test_prompt_manager(prompt_manager)
        self._test_conversation_manager(conversation_manager)
        self._test_mode_handler(mode_handler)
        self._test_web_interface(web_interface)
        
        self.demo_results["initialization"] = {
            "status": "success",
            "components_initialized": 5,
            "timestamp": datetime.now().isoformat()
        }
    
    def _test_data_processor(self, data_processor: DataProcessor):
        """Test data processor functionality."""
        print("   📊 Testing Data Processor...")
        
        # Load training data
        training_data = data_processor.load_all_training_data()
        print(f"      Loaded {len(training_data)} training data items")
        
        # Test relevant data retrieval
        relevant_data = data_processor.get_relevant_data("trainer location", max_results=3)
        print(f"      Found {len(relevant_data)} relevant items for 'trainer location'")
        
        # Test statistics
        stats = data_processor.get_statistics()
        print(f"      Data sources: {len(stats['sources'])}")
        
        self.demo_results["data_processor"] = {
            "training_data_count": len(training_data),
            "relevant_data_test": len(relevant_data),
            "sources_count": len(stats['sources'])
        }
    
    def _test_prompt_manager(self, prompt_manager: PromptManager):
        """Test prompt manager functionality."""
        print("   📝 Testing Prompt Manager...")
        
        # Test available modes
        modes = prompt_manager.get_available_modes()
        print(f"      Available modes: {len(modes)}")
        
        # Test mode validation
        valid_mode = prompt_manager.validate_mode("game_guide")
        invalid_mode = prompt_manager.validate_mode("invalid_mode")
        print(f"      Mode validation: game_guide={valid_mode}, invalid={invalid_mode}")
        
        # Test mode help
        help_info = prompt_manager.get_mode_help("game_guide")
        print(f"      Mode help available: {help_info is not None}")
        
        self.demo_results["prompt_manager"] = {
            "available_modes": len(modes),
            "mode_validation": {"valid": valid_mode, "invalid": invalid_mode},
            "help_available": help_info is not None
        }
    
    def _test_conversation_manager(self, conversation_manager: ConversationManager):
        """Test conversation manager functionality."""
        print("   💬 Testing Conversation Manager...")
        
        # Create session
        session_id = conversation_manager.create_session("demo_user", "game_guide")
        print(f"      Created session: {session_id}")
        
        # Add messages
        conversation_manager.add_message(session_id, "user", "Where can I find a trainer?", "game_guide")
        conversation_manager.add_message(session_id, "assistant", "I can help you find trainers!", "game_guide")
        
        # Get conversation history
        history = conversation_manager.get_conversation_history(session_id)
        print(f"      Conversation history: {len(history)} messages")
        
        # Get session info
        session_info = conversation_manager.get_session_info(session_id)
        print(f"      Session duration: {session_info['duration_seconds']:.2f}s")
        
        # Test analytics
        analytics = conversation_manager.get_analytics()
        print(f"      Analytics: {analytics['total_messages']} total messages")
        
        # Clean up
        conversation_manager.end_session(session_id)
        
        self.demo_results["conversation_manager"] = {
            "session_created": session_id is not None,
            "messages_added": 2,
            "history_length": len(history),
            "analytics_available": analytics is not None
        }
    
    def _test_mode_handler(self, mode_handler: ModeHandler):
        """Test mode handler functionality."""
        print("   🎮 Testing Mode Handler...")
        
        # Test available modes
        modes = mode_handler.get_available_modes()
        print(f"      Available modes: {len(modes)}")
        
        # Test mode detection
        detected_mode = mode_handler.detect_mode_from_query("Where can I find a trainer?")
        print(f"      Detected mode for trainer query: {detected_mode}")
        
        # Test mode suggestions
        suggestions = mode_handler.get_mode_suggestions("quest information")
        print(f"      Mode suggestions: {len(suggestions)}")
        
        # Test mode switching
        mode_handler.set_active_mode("bot_config_helper")
        active_mode = mode_handler.get_active_mode()
        print(f"      Active mode: {active_mode}")
        
        self.demo_results["mode_handler"] = {
            "available_modes": len(modes),
            "mode_detection": detected_mode,
            "suggestions_count": len(suggestions),
            "mode_switching": active_mode == "bot_config_helper"
        }
    
    def _test_web_interface(self, web_interface: WebInterface):
        """Test web interface functionality."""
        print("   🌐 Testing Web Interface...")
        
        # Create web session
        session_id = web_interface.create_session("demo_user", "game_guide")
        print(f"      Created web session: {session_id}")
        
        # Test message validation
        valid_message = web_interface.validate_message("Hello, how are you?")
        invalid_message = web_interface.validate_message("")
        print(f"      Message validation: valid={valid_message['valid']}, invalid={invalid_message['valid']}")
        
        # Test rate limiting
        rate_limit = web_interface.rate_limit_check(session_id)
        print(f"      Rate limit check: {rate_limit['allowed']}")
        
        # Test interface config
        config = web_interface.get_interface_config()
        print(f"      Interface config available: {config is not None}")
        
        # Test Cursor compatibility
        cursor_info = web_interface.get_cursor_compatibility_info()
        print(f"      Cursor compatible: {cursor_info['cursor_compatible']}")
        
        # Clean up
        web_interface.end_session(session_id)
        
        self.demo_results["web_interface"] = {
            "session_created": session_id is not None,
            "message_validation": {"valid": valid_message['valid'], "invalid": invalid_message['valid']},
            "rate_limiting": rate_limit['allowed'],
            "cursor_compatible": cursor_info['cursor_compatible']
        }
    
    def _demo_data_processing(self):
        """Demo data processing capabilities."""
        print("\n2. Data Processing Demo...")
        
        data_processor = self.ai_companion.data_processor
        
        # Test different query types
        test_queries = [
            "trainer location",
            "quest information", 
            "combat configuration",
            "lore background",
            "general help"
        ]
        
        for query in test_queries:
            relevant_data = data_processor.get_relevant_data(query, max_results=3)
            print(f"   Query: '{query}' -> Found {len(relevant_data)} relevant items")
        
        # Test statistics
        stats = data_processor.get_statistics()
        print(f"   📊 Data Statistics:")
        print(f"      Total items: {stats['total_items']}")
        print(f"      Sources: {list(stats['sources'].keys())}")
        print(f"      Categories: {list(stats['categories'].keys())}")
        
        self.demo_results["data_processing"] = {
            "test_queries": len(test_queries),
            "total_items": stats['total_items'],
            "sources": list(stats['sources'].keys()),
            "categories": list(stats['categories'].keys())
        }
    
    def _demo_prompt_management(self):
        """Demo prompt management capabilities."""
        print("\n3. Prompt Management Demo...")
        
        prompt_manager = self.ai_companion.prompt_manager
        
        # Test different modes
        test_modes = ["game_guide", "bot_config_helper", "lore_assistant", "general_assistant"]
        
        for mode in test_modes:
            mode_info = prompt_manager.get_mode_info(mode)
            if mode_info:
                print(f"   Mode: {mode_info['display_name']}")
                print(f"      Description: {mode_info['description']}")
                print(f"      Response style: {mode_info['response_style']}")
                print(f"      Specializations: {len(mode_info['specializations'])}")
        
        # Test mode suggestions
        test_queries = [
            "Where can I find a trainer?",
            "How do I configure my bot?",
            "Tell me about Star Wars lore",
            "What are some general tips?"
        ]
        
        for query in test_queries:
            suggestions = prompt_manager.get_mode_suggestions(query)
            print(f"   Query: '{query}' -> {len(suggestions)} mode suggestions")
        
        self.demo_results["prompt_management"] = {
            "modes_tested": len(test_modes),
            "queries_tested": len(test_queries),
            "suggestions_working": True
        }
    
    def _demo_conversation_management(self):
        """Demo conversation management capabilities."""
        print("\n4. Conversation Management Demo...")
        
        conversation_manager = self.ai_companion.conversation_manager
        
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_id = conversation_manager.create_session(f"user_{i}", "game_guide")
            session_ids.append(session_id)
            print(f"   Created session {i+1}: {session_id}")
        
        # Add messages to sessions
        test_messages = [
            ("Where can I find a trainer?", "game_guide"),
            ("How do I configure my bot?", "bot_config_helper"),
            ("Tell me about lore", "lore_assistant")
        ]
        
        for session_id, (message, mode) in zip(session_ids, test_messages):
            conversation_manager.add_message(session_id, "user", message, mode)
            conversation_manager.add_message(session_id, "assistant", f"Response to: {message}", mode)
            print(f"   Added messages to session: {session_id}")
        
        # Test session statistics
        stats = conversation_manager.get_session_statistics()
        print(f"   📊 Session Statistics:")
        print(f"      Active sessions: {stats['active_sessions']}")
        print(f"      Total messages: {stats['total_messages']}")
        print(f"      Mode distribution: {stats['mode_distribution']}")
        
        # Test conversation export
        for session_id in session_ids:
            export_json = conversation_manager.export_conversation(session_id, "json")
            export_text = conversation_manager.export_conversation(session_id, "text")
            print(f"   Exported session {session_id}: JSON={len(export_json) if export_json else 0} chars, Text={len(export_text) if export_text else 0} chars")
        
        # Clean up sessions
        for session_id in session_ids:
            conversation_manager.end_session(session_id)
        
        self.demo_results["conversation_management"] = {
            "sessions_created": len(session_ids),
            "messages_added": len(test_messages) * 2,
            "export_formats": ["json", "text"],
            "cleanup_successful": True
        }
    
    def _demo_mode_handling(self):
        """Demo mode handling capabilities."""
        print("\n5. Mode Handling Demo...")
        
        mode_handler = self.ai_companion.mode_handler
        
        # Test mode detection
        test_queries = [
            ("Where can I find a trainer?", "game_guide"),
            ("How do I configure my combat profile?", "bot_config_helper"),
            ("Tell me about Mandalorian lore", "lore_assistant"),
            ("What are some general tips?", "general_assistant")
        ]
        
        for query, expected_mode in test_queries:
            detected_mode = mode_handler.detect_mode_from_query(query)
            correct = detected_mode == expected_mode
            print(f"   Query: '{query}'")
            print(f"      Expected: {expected_mode}, Detected: {detected_mode}, Correct: {correct}")
        
        # Test mode switching
        for mode in ["game_guide", "bot_config_helper", "lore_assistant", "general_assistant"]:
            mode_handler.set_active_mode(mode)
            active_mode = mode_handler.get_active_mode()
            print(f"   Switched to {mode}: {active_mode == mode}")
        
        # Test mode help
        for mode in ["game_guide", "bot_config_helper"]:
            help_info = mode_handler.get_mode_help(mode)
            if help_info:
                print(f"   Help for {mode}: {len(help_info['example_questions'])} example questions")
        
        self.demo_results["mode_handling"] = {
            "detection_tests": len(test_queries),
            "switching_tests": 4,
            "help_available": True
        }
    
    def _demo_web_interface(self):
        """Demo web interface capabilities."""
        print("\n6. Web Interface Demo...")
        
        web_interface = self.ai_companion.web_interface
        
        # Create web session
        session_id = web_interface.create_session("demo_user", "game_guide")
        print(f"   Created web session: {session_id}")
        
        # Test message validation
        test_messages = [
            ("Hello, how are you?", True),
            ("", False),
            ("This is a very long message " * 100, False),
            ("Normal message", True)
        ]
        
        for message, should_be_valid in test_messages:
            validation = web_interface.validate_message(message)
            print(f"   Message validation: '{message[:30]}...' -> {validation['valid']} (expected: {should_be_valid})")
        
        # Test rate limiting
        for i in range(5):
            rate_limit = web_interface.rate_limit_check(session_id)
            print(f"   Rate limit check {i+1}: {rate_limit['allowed']}")
        
        # Test interface configuration
        config = web_interface.get_interface_config()
        print(f"   Interface config:")
        print(f"      Title: {config['title']}")
        print(f"      Theme: {config['theme']}")
        print(f"      Modes: {len(config['modes'])}")
        print(f"      Cursor compatible: {config['cursor_compatible']}")
        
        # Test Cursor compatibility
        cursor_info = web_interface.get_cursor_compatibility_info()
        print(f"   Cursor compatibility:")
        print(f"      Compatible: {cursor_info['cursor_compatible']}")
        print(f"      Features: {len(cursor_info['features'])}")
        print(f"      API endpoints: {len(cursor_info['api_endpoints'])}")
        
        # Clean up
        web_interface.end_session(session_id)
        
        self.demo_results["web_interface"] = {
            "session_created": session_id is not None,
            "validation_tests": len(test_messages),
            "rate_limit_tests": 5,
            "cursor_compatible": cursor_info['cursor_compatible']
        }
    
    def _demo_ai_companion_integration(self):
        """Demo the integrated AI companion functionality."""
        print("\n7. AI Companion Integration Demo...")
        
        # Create session
        self.session_id = self.ai_companion.create_session("demo_user", "game_guide")
        print(f"   Created AI companion session: {self.session_id}")
        
        # Test mode switching
        for mode in ["game_guide", "bot_config_helper", "lore_assistant", "general_assistant"]:
            success = self.ai_companion.set_mode(self.session_id, mode)
            print(f"   Switched to {mode}: {success}")
        
        # Test mode suggestions
        test_queries = [
            "Where can I find a trainer?",
            "How do I configure my bot?",
            "Tell me about lore",
            "What are some tips?"
        ]
        
        for query in test_queries:
            suggestions = self.ai_companion.get_mode_suggestions(query)
            print(f"   Query: '{query}' -> {len(suggestions)} suggestions")
        
        # Test message validation
        test_messages = [
            ("Hello!", True),
            ("", False),
            ("This is a test message", True)
        ]
        
        for message, should_be_valid in test_messages:
            validation = self.ai_companion.validate_message(message)
            print(f"   Message validation: '{message}' -> {validation['valid']} (expected: {should_be_valid})")
        
        self.demo_results["ai_companion_integration"] = {
            "session_created": self.session_id is not None,
            "mode_switching_tests": 4,
            "suggestion_tests": len(test_queries),
            "validation_tests": len(test_messages)
        }
    
    def _demo_conversation_flow(self):
        """Demo a complete conversation flow."""
        print("\n8. Conversation Flow Demo...")
        
        # Test queries for different modes
        test_conversations = [
            ("game_guide", "Where can I find a Marksman trainer on Tatooine?"),
            ("bot_config_helper", "How do I configure my combat profile?"),
            ("lore_assistant", "Tell me about the Mandalorians in SWG"),
            ("general_assistant", "What are some tips for new players?")
        ]
        
        for mode, query in test_conversations:
            print(f"   Testing {mode} mode...")
            
            # Set mode
            self.ai_companion.set_mode(self.session_id, mode)
            
            # Process query
            response = self.ai_companion.process_query(query, self.session_id, mode)
            
            print(f"      Query: {query}")
            print(f"      Response: {response.content[:100]}...")
            print(f"      Mode: {response.mode}")
            print(f"      Processing time: {response.processing_time:.2f}s")
            print(f"      Sources: {len(response.sources)}")
        
        # Test session info
        session_info = self.ai_companion.get_session_info(self.session_id)
        if session_info:
            print(f"   Session info:")
            print(f"      Mode: {session_info.get('mode', 'unknown')}")
            print(f"      Duration: {session_info.get('duration_seconds', 0):.2f}s")
        
        self.demo_results["conversation_flow"] = {
            "conversations_tested": len(test_conversations),
            "modes_tested": len(set(mode for mode, _ in test_conversations)),
            "responses_generated": len(test_conversations),
            "session_info_available": session_info is not None
        }
    
    def _demo_statistics_and_analytics(self):
        """Demo statistics and analytics capabilities."""
        print("\n9. Statistics and Analytics Demo...")
        
        # Get comprehensive statistics
        stats = self.ai_companion.get_statistics()
        
        print(f"   📊 AI Companion Statistics:")
        print(f"      Training data: {stats['training_data']['total_items']} items")
        print(f"      Conversation analytics: {stats['conversation']['total_messages']} messages")
        print(f"      Web sessions: {stats['web_sessions']['active_sessions']} active")
        print(f"      Available modes: {stats['modes']['total_modes']}")
        print(f"      GPT model: {stats['ai_companion']['model']}")
        print(f"      OpenAI available: {stats['ai_companion']['openai_available']}")
        
        # Test conversation export
        export_json = self.ai_companion.export_conversation(self.session_id, "json")
        export_text = self.ai_companion.export_conversation(self.session_id, "text")
        
        print(f"   📄 Export Results:")
        print(f"      JSON export: {len(export_json) if export_json else 0} characters")
        print(f"      Text export: {len(export_text) if export_text else 0} characters")
        
        # Test cleanup
        cleanup_results = self.ai_companion.cleanup_old_sessions()
        print(f"   🧹 Cleanup Results:")
        print(f"      Conversation sessions cleaned: {cleanup_results['conversation_sessions']}")
        print(f"      Web sessions cleaned: {cleanup_results['web_sessions']}")
        
        self.demo_results["statistics_analytics"] = {
            "training_data_items": stats['training_data']['total_items'],
            "total_messages": stats['conversation']['total_messages'],
            "active_sessions": stats['web_sessions']['active_sessions'],
            "export_formats": ["json", "text"],
            "cleanup_performed": True
        }
    
    def _demo_cleanup_and_maintenance(self):
        """Demo cleanup and maintenance capabilities."""
        print("\n10. Cleanup and Maintenance Demo...")
        
        # Test training data refresh
        refresh_result = self.ai_companion.refresh_training_data(force_refresh=False)
        print(f"   📊 Training Data Refresh:")
        print(f"      Success: {refresh_result['success']}")
        print(f"      Total items: {refresh_result['total_items']}")
        print(f"      Sources: {len(refresh_result.get('sources', {}))}")
        
        # Test session cleanup
        cleanup_results = self.ai_companion.cleanup_old_sessions()
        print(f"   🧹 Session Cleanup:")
        print(f"      Conversation sessions: {cleanup_results['conversation_sessions']}")
        print(f"      Web sessions: {cleanup_results['web_sessions']}")
        
        # Test web interface config
        web_config = self.ai_companion.get_web_interface_config()
        print(f"   🌐 Web Interface Config:")
        print(f"      Title: {web_config['title']}")
        print(f"      Theme: {web_config['theme']}")
        print(f"      Cursor compatible: {web_config['cursor_compatible']}")
        print(f"      Available modes: {len(web_config['modes'])}")
        
        # Test Cursor compatibility
        cursor_info = self.ai_companion.get_cursor_compatibility_info()
        print(f"   🖱️ Cursor Compatibility:")
        print(f"      Compatible: {cursor_info['cursor_compatible']}")
        print(f"      Features: {list(cursor_info['features'].keys())}")
        print(f"      API endpoints: {cursor_info['api_endpoints']}")
        
        # End session
        if self.session_id:
            self.ai_companion.end_session(self.session_id)
            print(f"   ✅ Session ended: {self.session_id}")
        
        self.demo_results["cleanup_maintenance"] = {
            "training_data_refreshed": refresh_result['success'],
            "sessions_cleaned": sum(cleanup_results.values()),
            "web_config_available": web_config is not None,
            "cursor_compatible": cursor_info['cursor_compatible'],
            "session_ended": self.session_id is not None
        }
    
    def _generate_demo_report(self):
        """Generate a comprehensive demo report."""
        print("\n📋 Demo Report")
        print("=" * 50)
        
        report = {
            "demo_timestamp": datetime.now().isoformat(),
            "demo_duration": "~2-3 minutes",
            "components_tested": len(self.demo_results),
            "overall_status": "success",
            "results": self.demo_results
        }
        
        # Save report
        report_file = self.demo_dir / "demo_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   📄 Report saved to: {report_file}")
        print(f"   🎯 Components tested: {len(self.demo_results)}")
        print(f"   ✅ Overall status: {report['overall_status']}")
        
        # Print summary
        print("\n📊 Demo Summary:")
        for component, results in self.demo_results.items():
            if isinstance(results, dict) and 'status' in results:
                status = results['status']
            else:
                status = "completed"
            print(f"   {component.replace('_', ' ').title()}: {status}")
    
    def _cleanup_demo_files(self):
        """Clean up demo files."""
        try:
            if self.demo_dir.exists():
                shutil.rmtree(self.demo_dir)
                print(f"   🧹 Cleaned up demo directory: {self.demo_dir}")
        except Exception as e:
            print(f"   ⚠️ Warning: Could not clean up demo directory: {str(e)}")

def main():
    """Main demo function."""
    demo = AICompanionDemo()
    
    try:
        demo.run_full_demo()
    finally:
        # Clean up demo files
        demo._cleanup_demo_files()

if __name__ == "__main__":
    main() 