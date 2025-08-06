# MS11 Bot Quickstart Guide

## Introduction

MS11 is a powerful automation bot for Star Wars Galaxies that can help you with various tasks including combat automation, quest completion, resource gathering, and more. This guide will help you set up and configure your first MS11 bot.

## What is MS11?

MS11 is an automation tool that can assist with:

- **Combat Automation**: Auto-attack, healing, and buff management
- **Quest Automation**: Automated quest completion and progression
- **Resource Gathering**: Automated surveying and resource collection
- **Travel Automation**: Automated navigation and waypoint following
- **Chat Management**: Automated responses and communication

> **Important**: Always check your server's rules regarding automation tools. Some servers may have restrictions on bot usage.

## Prerequisites

### System Requirements

- Windows 10 or later
- Python 3.8 or higher
- SWG Restoration client installed
- Administrator privileges (for some features)

### Game Setup

- Ensure your SWG client is properly configured
- You should be able to log in successfully
- Have a character ready with basic equipment
- Some credits for initial setup

## Installation

### 1. Download MS11

```bash
# Clone the repository
git clone https://github.com/ms11-project/ms11.git
cd ms11

# Install dependencies
pip install -r requirements.txt
```

### 2. File Structure

After installation, you should have:

```
ms11/
├── src/
│   ├── main.py
│   ├── config/
│   └── core/
├── data/
├── docs/
└── requirements.txt
```

### 3. Installation Tips

- Make sure to run the installation in a directory where you have write permissions
- Run the installation as administrator if needed
- Verify all dependencies are installed correctly

## Configuration

### Basic Configuration

Create your main configuration file:

```json
{
    "character_name": "YourCharacterName",
    "enable_discord_relay": true,
    "discord_webhook_url": "your_webhook_url_here",
    "auto_launch_enabled": false,
    "session_timeout": 3600
}
```

### Character Settings

Configure your character name and basic settings for the bot to recognize your character:

- **character_name**: Must match your in-game character name exactly
- **enable_discord_relay**: Enable Discord notifications
- **discord_webhook_url**: Your Discord webhook URL for notifications
- **auto_launch_enabled**: Enable automatic bot launching
- **session_timeout**: Session timeout in seconds

### Discord Integration

Set up Discord relay for notifications and remote monitoring:

1. Create a Discord webhook in your server
2. Add the webhook URL to your config
3. Test the connection
4. Configure notification preferences

### Session Management

Configure session timeouts, auto-launch settings, and session tracking:

- **session_timeout**: How long sessions can run
- **auto_launch_enabled**: Start bot automatically
- **session_tracking**: Track session statistics

### Safety Settings

Set up safety features like auto-logout, emergency stops, and anti-detection measures:

- **auto_logout**: Automatically logout in emergencies
- **emergency_stop**: Hotkey to stop the bot immediately
- **anti_detection**: Measures to avoid detection

### Profile Configuration

Create a profile for your character's build and preferences:

```json
{
    "skill_build": "rifleman_medic",
    "combat_profile": "pve_focused",
    "auto_heal_threshold": 75,
    "preferred_weapons": ["T21", "E11"],
    "buffs_required": ["medical_enhance", "performance_enhance"]
}
```

## First Run

### 1. Start the Bot

```bash
python src/main.py
```

### 2. Initial Setup

The bot will guide you through:
- Character selection
- Basic configuration
- Safety settings
- Profile setup

### 3. Test Basic Functions

Test these functions to ensure everything works:
- Movement and navigation
- Combat and targeting
- Inventory management
- Chat functionality

### 4. First Run Tips

- Start with simple tasks
- Gradually increase complexity
- Always monitor the bot during initial runs
- Test in safe areas first

## Basic Commands

### Essential Commands

```bash
# Start a session
/start_session

# Stop current session
/stop_session

# Pause bot (emergency stop)
/pause

# Resume bot
/resume

# Check status
/status

# Help
/help
```

### Combat Commands

```bash
# Attack nearest target
/attack

# Heal self
/heal

# Use buff
/buff [buff_name]

# Switch weapons
/switch_weapon [weapon_name]
```

### Movement Commands

```bash
# Move to coordinates
/move [x] [y]

# Follow waypoint
/follow_waypoint [waypoint_name]

# Return to safe location
/return_safe
```

## Useful Macros

### Basic Combat Macros

- **Auto-Heal**: Automatically heal when health is low
- **Weapon Switch**: Switch weapons based on situation
- **Buff Management**: Automatically apply buffs

### Exploration Macros

- **Resource Survey**: Automatically survey for resources
- **Waypoint Following**: Follow predefined waypoints
- **Safe Travel**: Travel safely between locations

### Emergency Macros

- **Emergency Stop**: Immediately stop all bot activities
- **Safe Logout**: Logout safely in emergencies
- **Status Report**: Send status to Discord

## Troubleshooting

### Common Issues

#### Bot Not Starting
**Solution**: Check that Python is installed correctly and all dependencies are installed. Run `pip install -r requirements.txt` again.

#### Character Not Recognized
**Solution**: Verify your character name in the config file matches exactly. Check for typos and case sensitivity.

#### Combat Not Working
**Solution**: Ensure your character has the correct weapons equipped and sufficient ammunition. Check combat profile settings.

#### Discord Not Connecting
**Solution**: Verify your Discord webhook URL is correct and the bot has proper permissions in your Discord server.

#### Performance Issues
**Solution**: Close unnecessary applications, check your internet connection, and consider reducing bot complexity.

### Getting Help

If you're still having issues:

1. **Check Documentation**: Review the comprehensive documentation
2. **Community Discord**: Join the community Discord for support
3. **Log Files**: Review log files for error messages
4. **FAQ**: Search the FAQ for common solutions

## Advanced Features

### Multi-Character Management

Once you're comfortable with the basics:

- Run multiple characters simultaneously
- Coordinate between characters
- Share resources and equipment

### Advanced Combat Profiles

Create complex combat strategies:

- Custom ability rotations
- Advanced positioning
- Complex buff management

### Quest Automation

Automate complex quest chains:

- Multi-step quest completion
- Resource gathering for quests
- Quest chain progression

### Resource Management

Automated resource gathering and crafting:

- Survey automation
- Resource collection
- Crafting automation

### Guild Integration

Coordinate with guild activities:

- Guild event participation
- Resource sharing
- Coordinated activities

## Safety and Best Practices

### Server Rules

- Always check your server's rules regarding automation
- Some servers have specific restrictions
- Respect server policies and community guidelines

### Anti-Detection

- Use random delays between actions
- Vary movement patterns
- Avoid predictable behavior
- Monitor for detection warnings

### Resource Management

- Don't overload your system
- Monitor CPU and memory usage
- Close unnecessary applications
- Use appropriate session timeouts

### Community Guidelines

- Be respectful to other players
- Don't interfere with other players' gameplay
- Report bugs and issues appropriately
- Contribute to the community positively

## Recommended Resources

### Documentation
- **Advanced Configuration**: Detailed configuration guides
- **Custom Scripting**: Learn to create custom scripts
- **API Reference**: Complete API documentation

### Community
- **Discord Server**: Real-time community support
- **Forums**: Community discussions and help
- **GitHub**: Source code and issues

### Tools
- **Build Browser**: Find compatible builds
- **Macro Library**: Pre-made macros and scripts
- **Configuration Templates**: Ready-to-use configs

## Conclusion

MS11 is a powerful tool that can enhance your SWG experience when used responsibly. Take your time to learn the basics, practice in safe environments, and always respect server rules and community guidelines.

Remember: The goal is to enhance your gameplay, not replace it entirely. Use MS11 as a tool to help you enjoy SWG more, not as a replacement for active gameplay.

---

*This guide is part of the SWGDB Getting Started section. For more detailed information, visit the other guides in this section.* 