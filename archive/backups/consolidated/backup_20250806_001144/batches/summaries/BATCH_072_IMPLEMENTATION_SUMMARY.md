# Batch 072 - Buff Advisor + Stat-Based Build Recommender

## Overview

Batch 072 implements a comprehensive buff advisor system that analyzes character stats and provides intelligent recommendations for buff food, entertainer dances, and armor setups. The system integrates with the build awareness from Batch 070 and stat optimizer from Batch 071 to provide context-aware recommendations.

## Features Implemented

### 1. Character Stat Analysis
- **Stat Log Parsing**: Parse character stats from `/stats` log entries using regex patterns
- **Stat Distribution Analysis**: Analyze total stats, averages, weakest/strongest stats, and optimization opportunities
- **Optimization Priorities**: Calculate priority scores for different optimization types (PvE damage, healing, buff stacking, balanced)
- **Stat Level Categorization**: Categorize stats as low, medium, high, or excellent based on thresholds

### 2. Buff Recommendations
- **Buff Food Recommendations**: Suggest specific food items based on stat needs and budget
- **Entertainer Dance Recommendations**: Recommend appropriate dances with stat bonuses and entertainer level requirements
- **Budget Filtering**: Filter recommendations based on cost (low, medium, high)
- **Combined Recommendations**: Provide comprehensive buff recommendations with expected improvements

### 3. Template Recommendations
- **Armor Setup Recommendations**: Suggest armor templates based on profession, combat style, and optimization goals
- **Weapon Setup Recommendations**: Recommend weapons based on build data and character stats
- **Budget-Aware Selection**: Choose appropriate templates within budget constraints
- **Stat Bonus Calculation**: Calculate total expected stat improvements from armor and weapon setups

### 4. Build Integration
- **Build Awareness Integration**: Integrate with Batch 070 build awareness system
- **Stat Optimizer Integration**: Connect with Batch 071 stat optimizer for comprehensive analysis
- **Build Compatibility Validation**: Validate if current stats are compatible with the build
- **Profession-Specific Recommendations**: Provide recommendations tailored to specific professions

## Architecture

### Core Components

#### 1. CharacterStatAnalyzer (`modules/buff_advisor/stat_analyzer.py`)
```python
class CharacterStatAnalyzer:
    """Analyzes character stats for buff and template recommendations."""
    
    def parse_stats_log(self, log_content: str) -> Dict[str, int]:
        """Parse character stats from a /stats log entry."""
    
    def analyze_stat_distribution(self, stats: Dict[str, int]) -> Dict[str, Any]:
        """Analyze the distribution of character stats."""
    
    def get_optimization_priorities(self, stats: Dict[str, int], 
                                   optimization_type: str = "balanced") -> List[Dict[str, Any]]:
        """Get optimization priorities based on stat goals."""
```

**Key Features:**
- Regex-based stat parsing from log content
- Comprehensive stat distribution analysis
- Priority scoring for different optimization types
- Stat level categorization (low/medium/high/excellent)

#### 2. BuffRecommender (`modules/buff_advisor/buff_recommender.py`)
```python
class BuffRecommender:
    """Recommends buff food and entertainer dances based on character stats."""
    
    def recommend_buff_food(self, stats: Dict[str, int], 
                           optimization_type: str = "balanced",
                           budget: str = "medium") -> List[Dict[str, Any]]:
        """Recommend buff food based on character stats and optimization goals."""
    
    def recommend_entertainer_dances(self, stats: Dict[str, int],
                                    optimization_type: str = "balanced",
                                    budget: str = "medium") -> List[Dict[str, Any]]:
        """Recommend entertainer dances based on character stats and optimization goals."""
```

**Key Features:**
- Comprehensive buff food database with stat bonuses and costs
- Entertainer dance recommendations with level requirements
- Budget-based filtering of recommendations
- Priority-based recommendation ordering

#### 3. TemplateRecommender (`modules/buff_advisor/template_recommender.py`)
```python
class TemplateRecommender:
    """Recommends armor setups based on character stats and build awareness."""
    
    def recommend_armor_setup(self, stats: Dict[str, int],
                              build_data: Dict[str, Any] = None,
                              optimization_type: str = "balanced",
                              budget: str = "medium") -> Dict[str, Any]:
        """Recommend armor setup based on character stats and build data."""
    
    def recommend_weapon_setup(self, stats: Dict[str, int],
                               build_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Recommend weapon setup based on character stats and build data."""
```

**Key Features:**
- Profession-specific armor templates (rifleman, pistoleer, medic, healer, balanced)
- Weapon setup recommendations based on build data
- Budget-aware template selection
- Comprehensive stat bonus calculations

#### 4. BuildIntegration (`modules/buff_advisor/build_integration.py`)
```python
class BuildIntegration:
    """Integrates buff advisor with build awareness system."""
    
    def get_build_data(self, character_name: str = None) -> Dict[str, Any]:
        """Get current build data from build awareness system."""
    
    def analyze_with_build_context(self, stats: Dict[str, int],
                                   character_name: str = None,
                                   optimization_type: str = "balanced") -> Dict[str, Any]:
        """Analyze stats with build context from Batch 070."""
    
    def validate_build_compatibility(self, stats: Dict[str, int],
                                    build_data: Dict[str, Any],
                                    optimization_type: str = "balanced") -> Dict[str, Any]:
        """Validate if current stats are compatible with the build."""
```

**Key Features:**
- Integration with Batch 070 build awareness system
- Build compatibility validation
- Profession and weapon compatibility checking
- Comprehensive build-aware analysis

#### 5. BuffAdvisor (`modules/buff_advisor/buff_advisor.py`)
```python
class BuffAdvisor:
    """Main buff advisor that orchestrates all recommendation components."""
    
    def analyze_character_and_recommend(self, stats_input: Dict[str, int] | str,
                                       character_name: str = None,
                                       optimization_type: str = "balanced",
                                       budget: str = "medium",
                                       include_build_awareness: bool = True) -> Dict[str, Any]:
        """Analyze character stats and provide comprehensive recommendations."""
    
    def analyze_from_stats_log(self, log_content: str,
                               character_name: str = None,
                               optimization_type: str = "balanced",
                               budget: str = "medium") -> Dict[str, Any]:
        """Analyze character from a /stats log entry."""
```

**Key Features:**
- Main orchestration component
- Comprehensive analysis and recommendations
- Stats log parsing support
- Export capabilities
- Recommendation history tracking

## Data Structures

### Buff Food Data
```python
buff_food_data = {
    "strength_food": {
        "items": ["Ryshcate", "Spiced Tea", "Caf", "Corellian Brandy"],
        "stat_bonus": {"strength": 25, "constitution": 10},
        "duration": 3600,  # 1 hour
        "cost": "medium"
    },
    # ... other food types
}
```

### Entertainer Dance Data
```python
entertainer_dances = {
    "strength_dance": {
        "name": "Might Dance",
        "stat_bonus": {"strength": 30, "constitution": 15},
        "duration": 7200,  # 2 hours
        "entertainer_level": "master",
        "cost": "high"
    },
    # ... other dances
}
```

### Armor Templates
```python
armor_templates = {
    "rifleman": {
        "name": "Rifleman Combat Armor",
        "slots": {
            "head": {"stat_bonus": {"agility": 15, "stamina": 10}},
            "chest": {"stat_bonus": {"strength": 20, "constitution": 15}},
            # ... other slots
        },
        "set_bonus": {"agility": 25, "stamina": 20},
        "combat_style": "ranged",
        "cost": "medium"
    },
    # ... other templates
}
```

## Integration Points

### 1. Batch 070 Integration
- **Build Awareness**: Uses `core.build_aware_behavior.BuildAwareBehavior` for build data
- **Profession Detection**: Leverages profession information for template selection
- **Combat Style Awareness**: Adapts recommendations based on combat style (ranged/melee/support)

### 2. Batch 071 Integration
- **Stat Optimizer**: Integrates with `modules.stat_optimizer.StatOptimizer` for comprehensive analysis
- **Google Sheets Data**: Can leverage external stat thresholds from Google Sheets
- **Alert System**: Connects with Discord alerts for suboptimal stat pools

### 3. Existing Systems Integration
- **Logging**: Uses `android_ms11.utils.logging_utils.log_event` for comprehensive logging
- **Error Handling**: Graceful error handling with fallback to default values
- **File Export**: JSON export capabilities for recommendation reports

## Usage Examples

### Basic Character Analysis
```python
from modules.buff_advisor import create_buff_advisor

advisor = create_buff_advisor()

# Analyze from stats dictionary
stats = {
    "strength": 95, "agility": 110, "constitution": 105,
    "stamina": 88, "mind": 120, "focus": 115, "willpower": 92
}

results = advisor.analyze_character_and_recommend(
    stats, "TestPlayer", "pve_damage", "medium", True
)
```

### Stats Log Analysis
```python
# Analyze from /stats log content
stats_log = """
Character: TestPlayer
Strength: 95
Agility: 110
Constitution: 105
Stamina: 88
Mind: 120
Focus: 115
Willpower: 92
"""

results = advisor.analyze_from_stats_log(
    stats_log, "TestPlayer", "pve_damage", "medium"
)
```

### Build Compatibility Report
```python
# Get build compatibility report
report = advisor.get_build_compatibility_report(
    stats, "TestPlayer", "balanced"
)
```

## Testing

### Test Coverage
- **29 comprehensive tests** covering all components
- **Unit tests** for each component (CharacterStatAnalyzer, BuffRecommender, TemplateRecommender, BuildIntegration, BuffAdvisor)
- **Integration tests** for complete workflow
- **Error handling tests** for edge cases
- **Different optimization types** testing

### Test Categories
1. **CharacterStatAnalyzer Tests**: Stat parsing, distribution analysis, optimization priorities
2. **BuffRecommender Tests**: Buff food and entertainer dance recommendations
3. **TemplateRecommender Tests**: Armor and weapon setup recommendations
4. **BuildIntegration Tests**: Build awareness integration and compatibility validation
5. **BuffAdvisor Tests**: Main orchestration and error handling
6. **Integration Tests**: Complete workflow and different optimization types

## Demo Script

The `demo_batch_072_buff_advisor.py` script demonstrates:
- Character stat analysis from /stats logs
- Buff food and entertainer dance recommendations
- Armor and weapon setup suggestions
- Build-aware compatibility analysis
- Integration with stat optimizer and build awareness
- Comprehensive reporting and export capabilities

## Files Created

### Core Module Files
- `modules/buff_advisor/__init__.py` - Module initialization and exports
- `modules/buff_advisor/stat_analyzer.py` - Character stat analysis
- `modules/buff_advisor/buff_recommender.py` - Buff food and dance recommendations
- `modules/buff_advisor/template_recommender.py` - Armor and weapon setup recommendations
- `modules/buff_advisor/build_integration.py` - Build awareness integration
- `modules/buff_advisor/buff_advisor.py` - Main orchestration component

### Demo and Test Files
- `demo_batch_072_buff_advisor.py` - Comprehensive demo script
- `test_batch_072_buff_advisor.py` - Complete test suite (29 tests)

## Key Benefits

1. **Comprehensive Analysis**: Provides complete character analysis with stat distribution and optimization priorities
2. **Context-Aware Recommendations**: Integrates with build awareness for profession-specific recommendations
3. **Budget Flexibility**: Supports different budget levels (low/medium/high) for recommendations
4. **Multiple Input Methods**: Supports both direct stats input and /stats log parsing
5. **Export Capabilities**: JSON export for recommendation reports
6. **Error Handling**: Graceful handling of invalid inputs with fallback to default values
7. **Integration Ready**: Designed to integrate with existing Batch 070 and 071 systems
8. **Extensible Architecture**: Modular design allows easy addition of new recommendation types

## Future Enhancements

1. **Real-time Integration**: Connect with live game data for real-time recommendations
2. **Machine Learning**: Implement ML-based recommendation optimization
3. **Advanced Budgeting**: More sophisticated budget management and cost optimization
4. **Performance Tracking**: Track recommendation effectiveness over time
5. **Community Features**: Share and rate recommendations with other players
6. **Mobile Support**: Mobile-friendly interface for recommendations
7. **Advanced Analytics**: Detailed analytics on stat optimization effectiveness

## Conclusion

Batch 072 successfully implements a comprehensive buff advisor system that provides intelligent recommendations for character optimization. The system integrates seamlessly with existing build awareness and stat optimizer systems, providing context-aware recommendations that adapt to different professions, combat styles, and optimization goals.

The modular architecture ensures maintainability and extensibility, while comprehensive testing ensures reliability. The system is ready for integration with the broader MS11 automation framework and provides a solid foundation for future enhancements. 