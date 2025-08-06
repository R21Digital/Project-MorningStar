#!/usr/bin/env python3
"""
Build Analyzer CLI
Command-line interface for the Build Analyzer Assistant (AskMrRoboto Alpha)
"""

import json
import sys
import os
import argparse
from typing import Dict, Optional

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.build_analyzer import BuildAnalyzer, format_build_report


class BuildAnalyzerCLI:
    """Command-line interface for the Build Analyzer"""
    
    def __init__(self):
        self.analyzer = BuildAnalyzer()
    
    def analyze_from_json(self, json_file: str) -> None:
        """Analyze a character from a JSON file"""
        try:
            with open(json_file, 'r') as f:
                character_data = json.load(f)
            
            print(f"Analyzing character from {json_file}...")
            report = format_build_report(character_data)
            print(report)
            
        except FileNotFoundError:
            print(f"Error: File '{json_file}' not found")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file '{json_file}'")
        except Exception as e:
            print(f"Error analyzing character: {e}")
    
    def analyze_interactive(self) -> None:
        """Interactive character analysis"""
        print("=== Build Analyzer Assistant (Interactive Mode) ===")
        print()
        
        # Get character name
        name = input("Character name: ").strip()
        if not name:
            name = "Unknown"
        
        # Get profession
        print("\nAvailable professions:")
        professions = ["rifleman", "pistoleer", "medic", "brawler"]
        for i, prof in enumerate(professions, 1):
            print(f"  {i}. {prof}")
        
        while True:
            try:
                prof_choice = input(f"\nSelect profession (1-{len(professions)}): ").strip()
                prof_index = int(prof_choice) - 1
                if 0 <= prof_index < len(professions):
                    profession = professions[prof_index]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Get role
        print("\nAvailable roles:")
        roles = ["tank", "dps", "healer", "support"]
        for i, role in enumerate(roles, 1):
            print(f"  {i}. {role}")
        
        while True:
            try:
                role_choice = input(f"\nSelect role (1-{len(roles)}): ").strip()
                role_index = int(role_choice) - 1
                if 0 <= role_index < len(roles):
                    role = roles[role_index]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Get stats
        print("\nEnter character stats (press Enter to skip):")
        stats = {}
        
        stat_names = ["damage", "accuracy", "critical", "constitution", "stamina", "defense", "healing"]
        stat_descriptions = {
            "damage": "Damage output",
            "accuracy": "Hit chance and precision",
            "critical": "Critical hit chance and damage",
            "constitution": "Health pool and regeneration",
            "stamina": "Energy pool and recovery",
            "defense": "Damage reduction and avoidance",
            "healing": "Healing output and efficiency"
        }
        
        for stat in stat_names:
            while True:
                value = input(f"{stat.title()} ({stat_descriptions[stat]}): ").strip()
                if not value:
                    break
                try:
                    stats[stat] = int(value)
                    break
                except ValueError:
                    print("Please enter a valid number.")
        
        # Create character data
        character_data = {
            "name": name,
            "profession": profession,
            "role": role,
            "stats": stats
        }
        
        # Analyze and display results
        print("\n" + "="*60)
        print("ANALYZING CHARACTER...")
        print("="*60)
        
        try:
            report = format_build_report(character_data)
            print(report)
        except Exception as e:
            print(f"Error during analysis: {e}")
    
    def create_sample_json(self, output_file: str = "sample_character.json") -> None:
        """Create a sample character JSON file"""
        sample_character = {
            "name": "SampleCharacter",
            "profession": "rifleman",
            "role": "dps",
            "stats": {
                "damage": 180,
                "accuracy": 150,
                "critical": 80,
                "constitution": 120,
                "stamina": 100
            }
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(sample_character, f, indent=2)
            print(f"Sample character file created: {output_file}")
            print("You can edit this file and use it with the --json option.")
        except Exception as e:
            print(f"Error creating sample file: {e}")
    
    def list_roles_and_professions(self) -> None:
        """List available roles and professions"""
        print("=== Available Roles and Professions ===")
        print()
        
        print("ROLES:")
        roles = ["tank", "dps", "healer", "support"]
        for role in roles:
            print(f"  - {role}")
        
        print("\nPROFESSIONS:")
        professions = ["rifleman", "pistoleer", "medic", "brawler"]
        for prof in professions:
            print(f"  - {prof}")
        
        print("\nSTATS:")
        stats = ["damage", "accuracy", "critical", "constitution", "stamina", "defense", "healing"]
        for stat in stats:
            print(f"  - {stat}")
    
    def show_help(self) -> None:
        """Show detailed help information"""
        help_text = """
Build Analyzer Assistant (AskMrRoboto Alpha) - CLI

USAGE:
  python build_analyzer_cli.py [OPTIONS]

OPTIONS:
  --json FILE          Analyze character from JSON file
  --interactive        Run in interactive mode
  --sample             Create sample character JSON file
  --list               List available roles and professions
  --help-detailed      Show detailed help message

EXAMPLES:
  # Interactive mode
  python build_analyzer_cli.py --interactive
  
  # Analyze from JSON file
  python build_analyzer_cli.py --json my_character.json
  
  # Create sample file
  python build_analyzer_cli.py --sample
  
  # List available options
  python build_analyzer_cli.py --list
  
  # Show detailed help
  python build_analyzer_cli.py --help-detailed

JSON FORMAT:
  {
    "name": "CharacterName",
    "profession": "rifleman",
    "role": "dps",
    "stats": {
      "damage": 180,
      "accuracy": 150,
      "critical": 80,
      "constitution": 120,
      "stamina": 100
    }
  }

FEATURES:
  - Stat optimization recommendations
  - Armor suggestions based on role and profession
  - Tape advice for optimal performance
  - Overall build scoring system
  - Priority improvement suggestions
  - Detailed analysis reports
        """
        print(help_text)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Build Analyzer Assistant (AskMrRoboto Alpha) - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_analyzer_cli.py --interactive
  python build_analyzer_cli.py --json my_character.json
  python build_analyzer_cli.py --sample
        """
    )
    
    parser.add_argument(
        '--json', 
        type=str, 
        help='Analyze character from JSON file'
    )
    parser.add_argument(
        '--interactive', 
        action='store_true', 
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--sample', 
        action='store_true', 
        help='Create sample character JSON file'
    )
    parser.add_argument(
        '--list', 
        action='store_true', 
        help='List available roles and professions'
    )
    parser.add_argument(
        '--help-detailed', 
        action='store_true', 
        help='Show detailed help'
    )
    
    args = parser.parse_args()
    
    cli = BuildAnalyzerCLI()
    
    if args.help_detailed:
        cli.show_help()
    elif args.json:
        cli.analyze_from_json(args.json)
    elif args.interactive:
        cli.analyze_interactive()
    elif args.sample:
        cli.create_sample_json()
    elif args.list:
        cli.list_roles_and_professions()
    else:
        # Default to interactive mode if no arguments provided
        cli.analyze_interactive()


if __name__ == "__main__":
    main() 