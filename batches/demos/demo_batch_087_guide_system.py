#!/usr/bin/env python3
"""
Demo script for Batch 087 - Public Guide Generator + Editor

This script demonstrates the guide system functionality by:
1. Creating sample guides with different categories and content
2. Testing the guide manager functionality
3. Starting the dashboard server for web interface testing
"""

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.guide_manager import GuideManager, GuideMetadata

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_guides():
    """Create sample guides for demonstration."""
    guide_manager = GuideManager()
    
    # Sample guide 1: Combat Guide
    combat_metadata = GuideMetadata(
        title="Combat Basics for Beginners",
        description="A comprehensive guide to combat mechanics in SWG, covering basic attacks, special abilities, and combat strategies.",
        keywords=["combat", "beginner", "attacks", "abilities", "strategy"],
        author="admin",
        created_date="",
        modified_date="",
        category="combat",
        tags=["combat", "beginner", "guide"],
        status="published",
        difficulty="beginner",
        estimated_read_time=10
    )
    
    combat_content = """# Combat Basics for Beginners

Welcome to the world of combat in Star Wars Galaxies! This guide will teach you the fundamentals of combat mechanics.

## Getting Started

Combat in SWG is turn-based and strategic. Here's what you need to know:

### Basic Attacks

- **Primary Attack**: Your main weapon attack
- **Secondary Attack**: Special weapon abilities
- **Unarmed Attack**: Hand-to-hand combat

### Combat Stats

Your character has several combat-related stats:

| Stat | Description |
|------|-------------|
| Health | Your life points |
| Action | Determines how many actions you can take |
| Mind | Affects special abilities |

### Combat Flow

1. **Initiative**: Determine who goes first
2. **Action Phase**: Choose your actions
3. **Resolution**: Actions are executed
4. **Repeat**: Continue until combat ends

## Tips for Success

- Always check your opponent's stats before engaging
- Use terrain to your advantage
- Keep healing items handy
- Practice with weaker enemies first

## Advanced Techniques

Once you've mastered the basics, try these advanced techniques:

### Positioning
- Use cover to reduce incoming damage
- Position yourself for flanking attacks
- Control chokepoints

### Ability Timing
- Save powerful abilities for critical moments
- Chain abilities together for maximum effect
- Monitor cooldowns carefully

Remember: Practice makes perfect! Start with simple encounters and gradually challenge yourself with tougher opponents.
"""
    
    combat_id = guide_manager.create_guide(combat_metadata, combat_content, "admin")
    logger.info(f"Created combat guide: {combat_id}")
    
    # Sample guide 2: Crafting Guide
    crafting_metadata = GuideMetadata(
        title="Crafting Mastery: From Novice to Expert",
        description="Learn the art of crafting in SWG, from basic resource gathering to creating masterwork items.",
        keywords=["crafting", "resources", "items", "masterwork", "profession"],
        author="admin",
        created_date="",
        modified_date="",
        category="crafting",
        tags=["crafting", "resources", "profession"],
        status="published",
        difficulty="intermediate",
        estimated_read_time=15
    )
    
    crafting_content = """# Crafting Mastery: From Novice to Expert

Crafting is one of the most rewarding activities in SWG. This guide will take you from beginner to expert crafter.

## Understanding Resources

### Resource Types

- **Organic**: Plants, animals, food
- **Inorganic**: Metals, minerals, chemicals
- **Energy**: Power sources, electronics

### Resource Quality

Resources have different quality levels:

- **Poor**: Basic materials
- **Average**: Standard quality
- **Good**: Above average
- **Excellent**: High quality
- **Exceptional**: Rare quality
- **Masterwork**: Perfect quality

## Crafting Process

### Step 1: Resource Gathering

1. **Survey**: Use survey tools to find resources
2. **Harvest**: Extract resources from nodes
3. **Transport**: Move resources to crafting facilities

### Step 2: Recipe Selection

Choose recipes based on:
- Available resources
- Market demand
- Skill requirements
- Profit potential

### Step 3: Crafting

1. **Setup**: Prepare your crafting station
2. **Execute**: Follow the recipe steps
3. **Quality Check**: Monitor the crafting process
4. **Completion**: Collect your finished item

## Advanced Techniques

### Resource Optimization

- **Blending**: Combine different resource qualities
- **Substitution**: Use alternative materials
- **Experimentation**: Try new combinations

### Market Analysis

- **Demand Tracking**: Monitor what sells
- **Price Analysis**: Understand market values
- **Competition Research**: Study other crafters

### Specialization

Focus on specific crafting types:
- **Weaponsmith**: Combat equipment
- **Armorsmith**: Protective gear
- **Chef**: Food and beverages
- **Architect**: Buildings and structures

## Tips for Success

1. **Start Small**: Begin with simple recipes
2. **Learn Markets**: Understand supply and demand
3. **Network**: Connect with other crafters
4. **Experiment**: Try new techniques
5. **Specialize**: Focus on profitable niches

## Common Mistakes to Avoid

- **Over-investing**: Don't spend too much on untested recipes
- **Ignoring Quality**: Always consider resource quality
- **Market Blindness**: Don't craft without checking demand
- **Skill Neglect**: Keep improving your crafting skills

Remember: Crafting is both an art and a business. Balance creativity with profitability!
"""
    
    crafting_id = guide_manager.create_guide(crafting_metadata, crafting_content, "admin")
    logger.info(f"Created crafting guide: {crafting_id}")
    
    # Sample guide 3: Travel Guide (Draft)
    travel_metadata = GuideMetadata(
        title="Efficient Travel in SWG",
        description="Learn the fastest and most efficient ways to travel across the galaxy, including shuttles, mounts, and personal vehicles.",
        keywords=["travel", "transportation", "shuttles", "mounts", "vehicles"],
        author="admin",
        created_date="",
        modified_date="",
        category="travel",
        tags=["travel", "transportation", "efficiency"],
        status="draft",
        difficulty="beginner",
        estimated_read_time=8
    )
    
    travel_content = """# Efficient Travel in SWG

Travel is essential in SWG. This guide covers all transportation options and how to use them efficiently.

## Transportation Options

### Shuttles
- **Starport Shuttles**: Inter-planetary travel
- **Local Shuttles**: Intra-planetary travel
- **Private Shuttles**: Player-owned transportation

### Mounts
- **Speeders**: Fast ground transportation
- **Animals**: Traditional mounts
- **Flying Mounts**: Aerial transportation

### Personal Vehicles
- **Speeders**: Personal ground vehicles
- **Ships**: Space travel
- **Special Vehicles**: Unique transportation

## Travel Tips

### Planning Your Route
1. **Check Schedules**: Know shuttle departure times
2. **Plan Stops**: Optimize your route
3. **Consider Costs**: Balance speed vs. expense
4. **Safety First**: Avoid dangerous areas

### Cost Optimization
- **Bulk Travel**: Group trips when possible
- **Off-Peak**: Travel during less busy times
- **Memberships**: Consider travel memberships
- **Alternatives**: Use cheaper options when possible

## Advanced Travel Techniques

### Speed Optimization
- **Shortcuts**: Learn faster routes
- **Combination Travel**: Mix different methods
- **Timing**: Travel during optimal conditions

### Safety Considerations
- **Route Planning**: Avoid dangerous areas
- **Backup Plans**: Have alternative routes
- **Emergency Contacts**: Know who to call for help

Remember: The journey is just as important as the destination!
"""
    
    travel_id = guide_manager.create_guide(travel_metadata, travel_content, "admin")
    logger.info(f"Created travel guide (draft): {travel_id}")
    
    return [combat_id, crafting_id, travel_id]

def test_guide_manager():
    """Test the guide manager functionality."""
    guide_manager = GuideManager()
    
    logger.info("Testing guide manager functionality...")
    
    # Test listing guides
    guides = guide_manager.list_guides()
    logger.info(f"Found {len(guides)} guides")
    
    # Test searching guides
    search_results = guide_manager.search_guides("combat")
    logger.info(f"Found {len(search_results)} guides matching 'combat'")
    
    # Test getting stats
    stats = guide_manager.get_stats()
    logger.info(f"Guide stats: {stats}")
    
    # Test getting categories
    categories = guide_manager.get_categories()
    logger.info(f"Available categories: {categories}")

def start_dashboard_server():
    """Start the dashboard server for web interface testing."""
    import subprocess
    import time
    
    logger.info("Starting dashboard server...")
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Start the Flask server
    try:
        process = subprocess.Popen([
            sys.executable, "dashboard/app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info("Dashboard server started!")
        logger.info("Access the guide system at: http://127.0.0.1:8000/guides")
        logger.info("Admin credentials: admin / admin123")
        logger.info("Press Ctrl+C to stop the server")
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("Stopping server...")
            process.terminate()
            process.wait()
            
    except Exception as e:
        logger.error(f"Error starting server: {e}")

def main():
    """Main demo function."""
    logger.info("Starting Batch 087 Guide System Demo")
    
    # Create sample guides
    logger.info("Creating sample guides...")
    guide_ids = create_sample_guides()
    
    # Test guide manager
    test_guide_manager()
    
    # Start dashboard server
    logger.info("Starting web interface...")
    start_dashboard_server()

if __name__ == "__main__":
    main() 