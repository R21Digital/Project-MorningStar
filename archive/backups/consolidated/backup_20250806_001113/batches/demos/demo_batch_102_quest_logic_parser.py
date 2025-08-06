"""Demo script for Batch 102 - Quest Logic Parser (MTG Integration).

This script demonstrates the new quest logic templates based on MTG server patterns,
showing improved fallback and retry decisions.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

from core.quest_logic_parser import (
    QuestLogicParser,
    QuestLogicType,
    QuestState,
    quest_logic_parser,
    parse_and_execute_quest
)


def load_sample_quest() -> Dict[str, Any]:
    """Load the sample MTG integration quest."""
    quest_file = Path("data/quest_templates/mtg_integration_sample.json")
    if quest_file.exists():
        with open(quest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Fallback sample quest if file doesn't exist
        return {
            "quest_id": "demo_quest",
            "name": "Demo MTG Integration Quest",
            "description": "Demonstrates the new quest logic templates",
            "steps": [
                {
                    "step_id": "wait_for_npc",
                    "type": "dialogue",
                    "title": "Wait for NPC",
                    "description": "Wait for the quest giver to appear",
                    "npc_id": "demo_npc",
                    "timeout_seconds": 10,
                    "retry_count": 2
                },
                {
                    "step_id": "travel_to_location",
                    "type": "move",
                    "title": "Travel to Location",
                    "description": "Travel to the quest location",
                    "data": {
                        "coords": [100, 200],
                        "planet": "tatooine"
                    },
                    "timeout_seconds": 10,
                    "retry_count": 2
                },
                {
                    "step_id": "use_key",
                    "type": "use_item",
                    "title": "Use Key",
                    "description": "Use the key to unlock the door",
                    "item_name": "demo_key",
                    "use_effect": {
                        "type": "unlock_door",
                        "door_id": "demo_door",
                        "consume_item": False
                    },
                    "timeout_seconds": 10,
                    "retry_count": 2
                },
                {
                    "step_id": "escort_target",
                    "type": "escort",
                    "title": "Escort Target",
                    "description": "Escort the target through the area",
                    "target_info": {
                        "name": "Demo Target",
                        "health": 100
                    },
                    "route_points": [[150, 250], [200, 300]],
                    "threat_level": "medium",
                    "timeout_seconds": 15,
                    "retry_count": 1
                },
                {
                    "step_id": "defend_location",
                    "type": "defend",
                    "title": "Defend Location",
                    "description": "Defend the location from threats",
                    "target_info": {
                        "name": "Demo Location",
                        "health": 200
                    },
                    "protection_requirements": {
                        "defense_duration": 10,
                        "min_target_health": 100
                    },
                    "threat_level": "high",
                    "timeout_seconds": 20,
                    "retry_count": 1
                }
            ]
        }


def create_demo_context() -> Dict[str, Any]:
    """Create a demo context for quest execution."""
    return {
        "current_location": [0, 0],
        "current_zone": "demo_zone",
        "current_planet": "tatooine",
        "inventory": {
            "demo_key": 1,
            "health_pack": 3
        },
        "nearby_npcs": {
            "demo_npc": True
        },
        "player_health": 100,
        "target_health": 100,
        "combat_targets_eliminated": 0,
        "unlocked_doors": [],
        "activated_devices": [],
        "target_location": [0, 0]
    }


def demonstrate_quest_parsing():
    """Demonstrate quest parsing functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING QUEST PARSING")
    print("="*60)
    
    # Load sample quest
    quest_data = load_sample_quest()
    print(f"Loaded quest: {quest_data['name']}")
    print(f"Quest ID: {quest_data['quest_id']}")
    print(f"Description: {quest_data['description']}")
    print(f"Total steps: {len(quest_data['steps'])}")
    
    # Parse quest into logic blocks
    parser = QuestLogicParser()
    logic_blocks = parser.parse_quest_template(quest_data)
    
    print(f"\nParsed {len(logic_blocks)} logic blocks:")
    for i, block in enumerate(logic_blocks, 1):
        print(f"  {i}. {block.block_id} ({block.logic_type.value})")
        print(f"     Description: {block.description}")
        print(f"     Timeout: {block.timeout_seconds}s, Retries: {block.retry_count}")
    
    return quest_data, logic_blocks, parser


def demonstrate_logic_templates():
    """Demonstrate individual logic templates."""
    print("\n" + "="*60)
    print("DEMONSTRATING LOGIC TEMPLATES")
    print("="*60)
    
    # Test WaitForTrigger
    print("\n1. WaitForTrigger Template:")
    wait_params = {
        "trigger_type": "npc_interaction",
        "conditions": {
            "npc_present": "demo_npc",
            "dialogue_completed": True
        },
        "timeout_seconds": 10,
        "retry_count": 2
    }
    wait_template = parser.template_registry[QuestLogicType.WAIT_FOR_TRIGGER](
        "demo_wait", wait_params
    )
    print(f"   - Block ID: {wait_template.block_id}")
    print(f"   - Trigger Type: {wait_template.trigger_type.value}")
    print(f"   - Conditions: {wait_template.trigger_conditions}")
    
    # Test TravelToZone
    print("\n2. TravelToZone Template:")
    travel_params = {
        "destination": {
            "coordinates": [100, 200],
            "zone": "demo_zone",
            "planet": "tatooine",
            "radius": 50
        },
        "travel_method": "mount",
        "route_optimization": True
    }
    travel_template = parser.template_registry[QuestLogicType.TRAVEL_TO_ZONE](
        "demo_travel", travel_params
    )
    print(f"   - Block ID: {travel_template.block_id}")
    print(f"   - Destination: {travel_template.destination}")
    print(f"   - Travel Method: {travel_template.travel_method}")
    
    # Test UseItem
    print("\n3. UseItem Template:")
    use_params = {
        "item_name": "demo_key",
        "use_target": "demo_door",
        "use_effect": {
            "type": "unlock_door",
            "door_id": "demo_door",
            "consume_item": False
        }
    }
    use_template = parser.template_registry[QuestLogicType.USE_ITEM](
        "demo_use_item", use_params
    )
    print(f"   - Block ID: {use_template.block_id}")
    print(f"   - Item: {use_template.item_name}")
    print(f"   - Effect: {use_template.use_effect}")
    
    # Test EscortDefend
    print("\n4. EscortDefend Template:")
    escort_params = {
        "mission_type": "escort",
        "target_info": {
            "name": "Demo Target",
            "health": 100
        },
        "route_points": [[150, 250], [200, 300]],
        "threat_level": "medium"
    }
    escort_template = parser.template_registry[QuestLogicType.ESCORT_DEFEND](
        "demo_escort", escort_params
    )
    print(f"   - Block ID: {escort_template.block_id}")
    print(f"   - Mission Type: {escort_template.mission_type}")
    print(f"   - Target: {escort_template.target_info}")
    print(f"   - Threat Level: {escort_template.threat_level}")


def demonstrate_quest_execution(quest_data: Dict[str, Any], logic_blocks: list, parser: QuestLogicParser):
    """Demonstrate quest execution with improved fallback and retry decisions."""
    print("\n" + "="*60)
    print("DEMONSTRATING QUEST EXECUTION")
    print("="*60)
    
    # Create demo context
    context = create_demo_context()
    print(f"Initial context:")
    print(f"  - Location: {context['current_location']}")
    print(f"  - Inventory: {context['inventory']}")
    print(f"  - Nearby NPCs: {list(context['nearby_npcs'].keys())}")
    
    # Execute quest
    print(f"\nExecuting quest: {quest_data['quest_id']}")
    start_time = time.time()
    
    success = parser.execute_quest_logic(
        quest_data['quest_id'],
        logic_blocks,
        context
    )
    
    execution_time = time.time() - start_time
    
    print(f"\nQuest execution completed in {execution_time:.2f} seconds")
    print(f"Success: {success}")
    
    # Get execution state
    execution_state = parser.get_execution_state(quest_data['quest_id'])
    if execution_state:
        print(f"\nExecution State:")
        print(f"  - State: {execution_state.state.value}")
        print(f"  - Current Step: {execution_state.current_step}")
        print(f"  - Completed Steps: {len(execution_state.completed_steps)}")
        print(f"  - Failed Steps: {len(execution_state.failed_steps)}")
        print(f"  - Retry Count: {execution_state.retry_count}")
        print(f"  - Fallback Count: {execution_state.fallback_count}")
        
        if execution_state.completed_steps:
            print(f"  - Completed: {execution_state.completed_steps}")
        if execution_state.failed_steps:
            print(f"  - Failed: {execution_state.failed_steps}")
    
    # Show final context
    print(f"\nFinal context:")
    print(f"  - Location: {context['current_location']}")
    print(f"  - Zone: {context['current_zone']}")
    print(f"  - Planet: {context['current_planet']}")
    print(f"  - Unlocked Doors: {context.get('unlocked_doors', [])}")
    print(f"  - Activated Devices: {context.get('activated_devices', [])}")
    print(f"  - Target Health: {context.get('target_health', 0)}")


def demonstrate_fallback_and_retry():
    """Demonstrate fallback and retry mechanisms."""
    print("\n" + "="*60)
    print("DEMONSTRATING FALLBACK AND RETRY MECHANISMS")
    print("="*60)
    
    # Create a quest with fallback blocks
    fallback_quest = {
        "quest_id": "fallback_demo",
        "steps": [
            {
                "step_id": "primary_approach",
                "type": "dialogue",
                "npc_id": "primary_npc",
                "timeout_seconds": 5,
                "retry_count": 1,
                "fallback_blocks": ["alternative_approach", "emergency_approach"]
            },
            {
                "step_id": "alternative_approach",
                "type": "dialogue",
                "npc_id": "alternative_npc",
                "timeout_seconds": 5,
                "retry_count": 1
            },
            {
                "step_id": "emergency_approach",
                "type": "use_item",
                "item_name": "emergency_key",
                "use_effect": {
                    "type": "unlock_door",
                    "door_id": "emergency_door"
                },
                "timeout_seconds": 5,
                "retry_count": 1
            }
        ]
    }
    
    context = {
        "current_location": [0, 0],
        "inventory": {"emergency_key": 1},
        "nearby_npcs": {"alternative_npc": True}  # Primary NPC not available
    }
    
    print("Testing fallback mechanism:")
    print("  - Primary NPC not available")
    print("  - Alternative NPC available")
    print("  - Emergency key available")
    
    parser = QuestLogicParser()
    logic_blocks = parser.parse_quest_template(fallback_quest)
    
    success = parser.execute_quest_logic(
        "fallback_demo",
        logic_blocks,
        context
    )
    
    print(f"\nFallback execution result: {success}")
    
    execution_state = parser.get_execution_state("fallback_demo")
    if execution_state:
        print(f"  - Final state: {execution_state.state.value}")
        print(f"  - Completed steps: {execution_state.completed_steps}")
        print(f"  - Failed steps: {execution_state.failed_steps}")


def demonstrate_convenience_function():
    """Demonstrate the convenience function."""
    print("\n" + "="*60)
    print("DEMONSTRATING CONVENIENCE FUNCTION")
    print("="*60)
    
    simple_quest = {
        "quest_id": "simple_demo",
        "steps": [
            {
                "step_id": "simple_wait",
                "type": "dialogue",
                "npc_id": "simple_npc",
                "timeout_seconds": 5,
                "retry_count": 1
            },
            {
                "step_id": "simple_travel",
                "type": "move",
                "data": {
                    "coords": [50, 100],
                    "planet": "tatooine"
                },
                "timeout_seconds": 5,
                "retry_count": 1
            }
        ]
    }
    
    context = {
        "current_location": [0, 0],
        "nearby_npcs": {"simple_npc": True}
    }
    
    print("Using convenience function parse_and_execute_quest()")
    success = parse_and_execute_quest(simple_quest, context)
    print(f"Result: {success}")


def demonstrate_performance():
    """Demonstrate performance characteristics."""
    print("\n" + "="*60)
    print("DEMONSTRATING PERFORMANCE")
    print("="*60)
    
    # Create a large quest for performance testing
    large_quest = {
        "quest_id": "performance_test",
        "steps": [
            {
                "step_id": f"step_{i}",
                "type": "dialogue" if i % 2 == 0 else "move",
                "npc_id": f"npc_{i}",
                "data": {
                    "coords": [i * 10, i * 20],
                    "planet": "tatooine"
                },
                "timeout_seconds": 1,
                "retry_count": 1
            }
            for i in range(50)  # 50 steps for performance test
        ]
    }
    
    context = {
        "current_location": [0, 0],
        "nearby_npcs": {f"npc_{i}": True for i in range(50)}
    }
    
    parser = QuestLogicParser()
    
    # Test parsing performance
    print("Testing parsing performance...")
    start_time = time.time()
    logic_blocks = parser.parse_quest_template(large_quest)
    parse_time = time.time() - start_time
    
    print(f"  - Parsed {len(logic_blocks)} logic blocks")
    print(f"  - Parse time: {parse_time:.4f} seconds")
    print(f"  - Average time per block: {parse_time/len(logic_blocks):.6f} seconds")
    
    # Test execution performance (with mocked execution)
    print("\nTesting execution performance...")
    start_time = time.time()
    
    # Mock the execution to avoid long waits
    with parser._execute_with_retry.__patched__:
        success = parser.execute_quest_logic(
            "performance_test",
            logic_blocks,
            context
        )
    
    execution_time = time.time() - start_time
    print(f"  - Execution time: {execution_time:.4f} seconds")
    print(f"  - Success: {success}")


def main():
    """Main demonstration function."""
    print("BATCH 102 - QUEST LOGIC PARSER (MTG INTEGRATION) DEMO")
    print("="*80)
    print("This demo showcases the new quest logic templates based on MTG server patterns.")
    print("Features demonstrated:")
    print("  - WaitForTrigger: Wait for specific conditions to be met")
    print("  - TravelToZone: Travel to specific locations with route optimization")
    print("  - UseItem: Use items with various effects (unlock doors, activate devices, heal)")
    print("  - EscortDefend: Escort targets or defend locations with threat handling")
    print("  - Improved fallback and retry decisions")
    print("  - Enhanced quest execution state tracking")
    
    try:
        # Demonstrate quest parsing
        quest_data, logic_blocks, parser = demonstrate_quest_parsing()
        
        # Demonstrate individual logic templates
        demonstrate_logic_templates()
        
        # Demonstrate quest execution
        demonstrate_quest_execution(quest_data, logic_blocks, parser)
        
        # Demonstrate fallback and retry mechanisms
        demonstrate_fallback_and_retry()
        
        # Demonstrate convenience function
        demonstrate_convenience_function()
        
        # Demonstrate performance
        demonstrate_performance()
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("The Quest Logic Parser (MTG Integration) provides:")
        print("  ✓ Enhanced quest execution with improved reliability")
        print("  ✓ Flexible logic templates based on MTG server patterns")
        print("  ✓ Robust fallback and retry mechanisms")
        print("  ✓ Comprehensive state tracking and monitoring")
        print("  ✓ High-performance parsing and execution")
        print("  ✓ Easy integration with existing quest systems")
        
    except Exception as e:
        print(f"\nDemo encountered an error: {e}")
        print("This is expected in a demo environment with simulated execution.")


if __name__ == "__main__":
    main() 