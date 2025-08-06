# Build Guides

This section provides comprehensive documentation for the Community Builds system, which allows users to select from pre-built combat and utility templates.

## Overview

The Community Builds system provides a collection of pre-configured character builds that can be imported and applied to your character. Each build includes:

- **Profession combinations** with skill progression paths
- **Equipment recommendations** including weapons, armor, and enhancements
- **Performance metrics** for different playstyles (PvE, PvP, Group, Solo)
- **Combat strategies** with ability rotations and cooldown management
- **Difficulty ratings** to help choose appropriate builds

## Available Builds

### Combat Builds

#### Rifleman/Medic
- **Difficulty**: Medium
- **Specialization**: PvE
- **Description**: Versatile combat build combining ranged damage with healing capabilities
- **Best For**: Solo PvE content, group support
- **Performance**: PvE 8.5/10, Solo 9.0/10, Group 8.0/10

**Key Features**:
- Excellent ranged combat capabilities
- Self-healing and group healing abilities
- Good survivability in solo play
- Requires careful positioning and distance management

**Equipment Recommendations**:
- Weapons: T21, T21B, E11
- Armor: Stormtrooper Armor, Mandalorian Armor
- Tapes: Accuracy, Damage, Critical
- Resists: Energy, Kinetic, Blast

#### Teras Kasi/Pistoleer
- **Difficulty**: Hard
- **Specialization**: PvP
- **Description**: Hybrid melee and ranged combat build with high mobility
- **Best For**: PvP combat, high-skill players
- **Performance**: PvP 9.0/10, Solo 8.5/10, Group 6.5/10

**Key Features**:
- Versatile combat style switching between melee and ranged
- High mobility and positioning flexibility
- Excellent for skilled PvP players
- Requires good timing and positioning

**Equipment Recommendations**:
- Weapons: Power Hammer, DL44, DH17
- Armor: Combat Armor, Reinforced Armor
- Tapes: Accuracy, Damage, Critical
- Resists: Kinetic, Energy

#### Commando/Medic
- **Difficulty**: Medium
- **Specialization**: Group
- **Description**: Heavy weapons specialist with strong healing support
- **Best For**: Group content, heroics, area damage
- **Performance**: PvE 9.0/10, Group 9.5/10, Solo 8.0/10

**Key Features**:
- Excellent area damage capabilities
- Strong group healing support
- Heavy weapon specialization
- Requires careful resource management

**Equipment Recommendations**:
- Weapons: T21, Heavy Rifle, E11
- Armor: Stormtrooper Armor, Mandalorian Armor
- Tapes: Damage, Accuracy, Critical
- Resists: Energy, Kinetic, Blast

### Utility Builds

#### Scout/Medic
- **Difficulty**: Easy
- **Specialization**: Solo
- **Description**: Stealth and reconnaissance specialist with healing abilities
- **Best For**: Solo exploration, farming, stealth gameplay
- **Performance**: Solo 9.5/10, PvE 8.0/10, Farming 8.0/10

**Key Features**:
- Excellent stealth capabilities
- Self-sufficient with healing
- Great for exploration and farming
- Best for avoiding combat when possible

**Equipment Recommendations**:
- Weapons: T21, E11, Carbine
- Armor: Scout Armor, Combat Armor
- Tapes: Accuracy, Stealth, Damage
- Resists: Energy, Kinetic

#### Brawler/Tank
- **Difficulty**: Medium
- **Specialization**: Tank
- **Description**: Melee tank build focused on damage absorption and close combat
- **Best For**: Group tanking, protecting other players
- **Performance**: Group 9.0/10, PvE 8.5/10, PvP 8.0/10

**Key Features**:
- High survivability and damage absorption
- Excellent for protecting group members
- Good aggro management capabilities
- Requires careful positioning and aggro management

**Equipment Recommendations**:
- Weapons: Power Hammer, Vibro Axe, Sword
- Armor: Tank Armor, Heavy Combat Armor
- Tapes: Defense, Health, Damage
- Resists: Kinetic, Energy, Blast

## Using Community Builds

### Selecting a Build

1. **Access the Build Selector**: Navigate to the Builds section in the dashboard
2. **Filter Builds**: Use the filters to narrow down builds by:
   - Category (Combat, Utility, Support)
   - Specialization (PvE, PvP, Group, Solo, Tank, Farming)
   - Difficulty (Easy, Medium, Hard)
3. **Review Performance**: Check the performance ratings for your intended playstyle
4. **View Details**: Click "View Details" to see comprehensive build information
5. **Select Build**: Click "Select Build" to apply the build to your character

### Build Information

Each build provides detailed information including:

- **Description**: Overview of the build's purpose and playstyle
- **Professions**: Primary and secondary profession combinations
- **Skills**: Complete skill progression path for each profession
- **Equipment**: Recommended weapons, armor, tapes, and resists
- **Performance**: Ratings for different playstyles (PvE, PvP, Solo, Group, Farming)
- **Combat Strategy**: Ability rotations, cooldowns, and combat tactics
- **Notes**: Important tips and considerations for the build

### Applying a Build

When you select a build, the system will:

1. **Load Skills**: Import the skill progression path into your training queue
2. **Update Equipment**: Provide recommendations for gear optimization
3. **Configure Combat**: Set up ability rotations and combat strategies
4. **Track Progress**: Monitor your progress through the build's skill path

## Performance Metrics

Builds are rated on a scale of 1-10 for different playstyles:

- **PvE Rating**: Effectiveness in player vs environment content
- **PvP Rating**: Effectiveness in player vs player combat
- **Solo Rating**: Ability to handle content independently
- **Group Rating**: Effectiveness in group/heroic content
- **Farming Rating**: Efficiency for resource gathering and farming

### Rating Guidelines

- **9-10**: Excellent performance, highly recommended
- **7-8**: Good performance, solid choice
- **5-6**: Average performance, acceptable but not optimal
- **3-4**: Below average, consider alternatives
- **1-2**: Poor performance, not recommended

## Difficulty Levels

### Easy
- Straightforward skill progression
- Simple combat rotations
- Forgiving resource management
- Good for beginners or casual players

### Medium
- Moderate complexity in skill choices
- More nuanced combat strategies
- Requires some resource management
- Suitable for experienced players

### Hard
- Complex skill combinations
- Advanced combat tactics
- Requires careful resource management
- Best for skilled players

## Creating Custom Builds

### Build Structure

Custom builds should follow this YAML structure:

```yaml
builds:
  your_build_name:
    name: "Your Build Name"
    description: "Description of your build"
    category: "combat"  # combat, utility, support
    specialization: "pve"  # pve, pvp, group, solo, tank, farming
    difficulty: "medium"  # easy, medium, hard
    
    professions:
      primary: "Primary Profession"
      secondary: "Secondary Profession"
    
    skills:
      profession_name:
        - "skill_1"
        - "skill_2"
        - "skill_3"
    
    equipment:
      weapons:
        primary: "weapon_type"
        secondary: "weapon_type"
        recommended:
          - "Weapon 1"
          - "Weapon 2"
      armor:
        type: "armor_type"
        recommended:
          - "Armor 1"
          - "Armor 2"
      tapes:
        - "tape_type_1"
        - "tape_type_2"
      resists:
        - "resist_type_1"
        - "resist_type_2"
    
    performance:
      pve_rating: 8.5
      pvp_rating: 6.0
      solo_rating: 9.0
      group_rating: 8.0
      farming_rating: 7.5
    
    combat:
      style: "ranged"  # ranged, melee, hybrid, stealth
      stance: "kneeling"  # kneeling, standing, crouching
      rotation:
        - "ability_1"
        - "ability_2"
        - "ability_3"
      heal_threshold: 50
      buff_threshold: 80
      max_range: 50
    
    cooldowns:
      ability_1: 0
      ability_2: 5
      ability_3: 15
    
    emergency_abilities:
      critical_heal: "heal_ability"
      defensive: "defensive_ability"
    
    notes:
      - "Important note 1"
      - "Important note 2"
```

### Best Practices

1. **Test Your Build**: Ensure the build works well in practice before sharing
2. **Provide Clear Descriptions**: Explain what the build is good for and its limitations
3. **Include Equipment Recommendations**: Help users optimize their gear
4. **Add Performance Ratings**: Be honest about the build's strengths and weaknesses
5. **Include Notes**: Share tips and strategies for using the build effectively

## Integration with Existing Systems

The Community Builds system integrates with several existing systems:

### Build Manager
- Loads and manages build definitions
- Provides build validation and error checking
- Exports builds to JSON format for compatibility

### Dashboard Integration
- Build selector component for easy browsing
- Filter and search capabilities
- Detailed build information display

### Combat System
- Automatic combat profile generation
- Ability rotation configuration
- Cooldown management

### Training System
- Automatic skill queue population
- Progress tracking through build paths
- XP requirement calculations

## Troubleshooting

### Common Issues

**Build Not Loading**
- Check that the YAML file is properly formatted
- Ensure all required fields are present
- Verify file permissions and location

**Performance Issues**
- Check that performance ratings are between 1-10
- Ensure all required combat fields are present
- Validate skill progression paths

**Equipment Conflicts**
- Verify weapon and armor type compatibility
- Check that recommended items exist in the game
- Ensure resist types are valid

### Getting Help

If you encounter issues with the Community Builds system:

1. **Check the Logs**: Look for error messages in the application logs
2. **Validate Your Build**: Use the build validation tools to check for issues
3. **Review Documentation**: Consult this guide and related documentation
4. **Community Support**: Ask for help in the community forums

## Future Enhancements

Planned improvements to the Community Builds system:

- **Build Sharing**: Allow users to share custom builds with the community
- **Build Ratings**: Community rating and review system for builds
- **Build Templates**: Pre-built templates for common build types
- **Advanced Filtering**: More sophisticated search and filter options
- **Build Analytics**: Usage statistics and performance tracking
- **Mobile Support**: Optimized interface for mobile devices

## Contributing

To contribute to the Community Builds system:

1. **Create Quality Builds**: Develop well-tested, documented builds
2. **Follow Standards**: Use the established YAML format and conventions
3. **Test Thoroughly**: Ensure builds work correctly in practice
4. **Document Clearly**: Provide clear descriptions and instructions
5. **Share Knowledge**: Help other users understand and use builds effectively

For more information about contributing, see the [Contributing Guide](../contributing.md). 