#!/usr/bin/env python3
"""
Demonstration script for Batch 030 - Travel via Starports & Personal Ships

This script demonstrates the terminal travel and ship travel functionality including:
- OCR-based terminal detection
- Waypoint navigation to terminals
- Destination selection from travel dialogs
- Personal ship travel with cooldown management
- Success/failure rate tracking
"""

import time
from pathlib import Path

# Import the travel modules
try:
    from travel.terminal_travel import (
        get_terminal_travel_system, scan_for_terminals, navigate_to_terminal,
        select_destination, get_travel_statistics, TerminalScanResult,
        TravelDialogResult, TerminalStatus
    )
    from travel.ship_travel import (
        get_ship_travel_system, check_ship_availability, auto_use_personal_ship,
        execute_ship_travel, get_ship_travel_statistics, ShipTravelResult,
        ShipStatus, ShipType
    )
    from travel.locations import TravelTerminal, TerminalType
    TRAVEL_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import travel modules: {e}")
    TRAVEL_MODULES_AVAILABLE = False


def demonstrate_terminal_travel():
    """Demonstrate terminal travel functionality."""
    if not TRAVEL_MODULES_AVAILABLE:
        print("Travel modules not available. Skipping terminal travel demonstration.")
        return
    
    print("=== Terminal Travel Demonstration ===\n")
    
    # Get terminal travel system
    terminal_system = get_terminal_travel_system()
    
    print("1. Terminal Travel System Initialization")
    print("-" * 45)
    print(f"OCR Available: {terminal_system.ocr_engine is not None}")
    print(f"Current Status: {terminal_system.current_status.value}")
    print(f"Scan Results: {len(terminal_system.scan_results)}")
    print(f"Travel History: {len(terminal_system.travel_history)}")
    print()
    
    # Demonstrate terminal scanning
    print("2. Terminal Scanning")
    print("-" * 25)
    
    # Scan for all terminals
    print("Scanning for all terminals...")
    scan_results = terminal_system.scan_for_terminals()
    
    if scan_results:
        print(f"Found {len(scan_results)} terminals:")
        for i, result in enumerate(scan_results, 1):
            print(f"  {i}. {result.terminal_name} ({result.terminal_type.value})")
            print(f"     Confidence: {result.confidence:.1f}%")
            print(f"     Coordinates: {result.coordinates}")
            print(f"     Scan Time: {result.scan_time:.2f}s")
            print()
    else:
        print("No terminals found (normal if not in game)")
        print()
    
    # Scan for specific terminal types
    print("Scanning for shuttleports...")
    shuttleport_results = terminal_system.scan_for_terminals(TerminalType.SHUTTLEPORT)
    print(f"Found {len(shuttleport_results)} shuttleports")
    
    print("Scanning for starports...")
    starport_results = terminal_system.scan_for_terminals(TerminalType.STARPORT)
    print(f"Found {len(starport_results)} starports")
    print()
    
    # Demonstrate terminal navigation
    print("3. Terminal Navigation")
    print("-" * 25)
    
    # Create a test terminal
    test_terminal = TravelTerminal(
        name="Test Shuttleport",
        city="test_city",
        planet="test_planet",
        terminal_type=TerminalType.SHUTTLEPORT,
        coordinates=(100, 200)
    )
    
    print(f"Navigating to {test_terminal.name}...")
    navigation_success = terminal_system.navigate_to_terminal(test_terminal)
    
    if navigation_success:
        print("✅ Navigation successful")
    else:
        print("❌ Navigation failed")
    print()
    
    # Demonstrate terminal interaction
    print("4. Terminal Interaction")
    print("-" * 25)
    
    print(f"Interacting with {test_terminal.name}...")
    interaction_success = terminal_system.interact_with_terminal(test_terminal)
    
    if interaction_success:
        print("✅ Terminal interaction successful")
    else:
        print("❌ Terminal interaction failed")
    print()
    
    # Demonstrate destination selection
    print("5. Destination Selection")
    print("-" * 25)
    
    route_info = {
        "dest_planet": "naboo",
        "dest_city": "theed"
    }
    
    print(f"Selecting destination: {route_info['dest_planet']} - {route_info['dest_city']}")
    dialog_result = terminal_system.select_destination(route_info)
    
    if dialog_result.dialog_detected:
        print("✅ Travel dialog detected")
        print(f"   Available destinations: {len(dialog_result.destinations_available or [])}")
        print(f"   Selected destination: {dialog_result.selected_destination}")
        print(f"   Confirmation required: {dialog_result.confirmation_required}")
        print(f"   Travel cost: {dialog_result.travel_cost}")
        print(f"   Travel time: {dialog_result.travel_time}")
    else:
        print("❌ Travel dialog not detected")
    print()
    
    # Demonstrate travel confirmation
    print("6. Travel Confirmation")
    print("-" * 25)
    
    if dialog_result.dialog_detected and dialog_result.selected_destination:
        print("Confirming travel...")
        confirmation_success = terminal_system.confirm_travel(dialog_result)
        
        if confirmation_success:
            print("✅ Travel confirmed successfully")
        else:
            print("❌ Travel confirmation failed")
    else:
        print("Skipping travel confirmation (no destination selected)")
    print()
    
    # Show travel statistics
    print("7. Travel Statistics")
    print("-" * 20)
    
    stats = terminal_system.get_travel_statistics()
    print(f"Total travels: {stats['total_travels']}")
    print(f"Successful travels: {stats['successful_travels']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    
    if stats['recent_travels']:
        print("\nRecent travels:")
        for travel in stats['recent_travels'][-3:]:  # Last 3
            print(f"  - {travel.get('destination', 'Unknown')} ({travel.get('status', 'Unknown')})")
    print()


def demonstrate_ship_travel():
    """Demonstrate ship travel functionality."""
    if not TRAVEL_MODULES_AVAILABLE:
        print("Travel modules not available. Skipping ship travel demonstration.")
        return
    
    print("=== Ship Travel Demonstration ===\n")
    
    # Get ship travel system
    ship_system = get_ship_travel_system()
    
    print("1. Ship Travel System Initialization")
    print("-" * 40)
    print(f"OCR Available: {ship_system.ocr_engine is not None}")
    print(f"Current Status: {ship_system.current_status.value}")
    print(f"Total Ships: {len(ship_system.ships)}")
    print(f"Travel History: {len(ship_system.travel_history)}")
    print()
    
    # Show available ships
    print("2. Available Ships")
    print("-" * 18)
    
    for ship_name, ship_info in ship_system.ships.items():
        status_icon = "✓" if ship_info.unlocked else "✗"
        print(f"{status_icon} {ship_info.ship_name} ({ship_info.ship_type.value})")
        print(f"   Unlocked: {ship_info.unlocked}")
        print(f"   Fuel Level: {ship_info.fuel_level}%")
        print(f"   Max Cooldown: {ship_info.max_cooldown}s")
        print()
    
    # Demonstrate ship availability checking
    print("3. Ship Availability Check")
    print("-" * 28)
    
    availability = ship_system.check_ship_availability()
    print(f"Available ships: {availability['total_available']}")
    print(f"Unavailable ships: {availability['total_unavailable']}")
    
    if availability['available_ships']:
        print("\nAvailable ships:")
        for ship in availability['available_ships']:
            print(f"  - {ship['name']} ({ship['type']})")
            print(f"    Fuel: {ship['fuel_level']}%")
            print(f"    Travel time: {ship['travel_time']}s")
    
    if availability['unavailable_ships']:
        print("\nUnavailable ships:")
        for ship in availability['unavailable_ships']:
            print(f"  - {ship['name']}: {ship['reason']}")
            if 'cooldown_remaining' in ship:
                print(f"    Cooldown: {ship['cooldown_remaining']}s")
            if 'fuel_level' in ship:
                print(f"    Fuel: {ship['fuel_level']}%")
    print()
    
    # Demonstrate ship scanning
    print("4. Ship Scanning")
    print("-" * 15)
    
    print("Scanning for ships using OCR...")
    detected_ships = ship_system.scan_for_ships()
    
    if detected_ships:
        print(f"Found {len(detected_ships)} ships:")
        for i, ship in enumerate(detected_ships, 1):
            print(f"  {i}. {ship['type']} (confidence: {ship['confidence']:.1f}%)")
    else:
        print("No ships detected via OCR (normal if not in ship interface)")
    print()
    
    # Demonstrate auto-use personal ship
    print("5. Auto-Use Personal Ship")
    print("-" * 28)
    
    destination = "naboo_theed"
    print(f"Attempting auto-use personal ship to {destination}...")
    
    result = ship_system.auto_use_personal_ship(destination)
    
    if result.success:
        print("✅ Ship travel successful")
        print(f"   Ship used: {result.ship_used}")
        print(f"   Travel time: {result.travel_time}s")
        print(f"   Fuel consumed: {result.fuel_consumed}%")
    else:
        print("❌ Ship travel failed")
        print(f"   Error: {result.error_message}")
    print()
    
    # Demonstrate specific ship travel
    print("6. Specific Ship Travel")
    print("-" * 24)
    
    # Try to travel with a specific ship
    ship_name = "x-wing"
    destination = "corellia_coronet"
    
    print(f"Attempting travel with {ship_name} to {destination}...")
    
    result = ship_system.execute_ship_travel(ship_name, destination)
    
    if result.success:
        print("✅ Ship travel successful")
        print(f"   Ship used: {result.ship_used}")
        print(f"   Travel time: {result.travel_time}s")
        print(f"   Fuel consumed: {result.fuel_consumed}%")
    else:
        print("❌ Ship travel failed")
        print(f"   Error: {result.error_message}")
    print()
    
    # Demonstrate ship management
    print("7. Ship Management")
    print("-" * 18)
    
    # Refuel a ship
    ship_name = "x-wing"
    print(f"Refueling {ship_name}...")
    refuel_success = ship_system.refuel_ship(ship_name)
    
    if refuel_success:
        print("✅ Ship refueled successfully")
    else:
        print("❌ Ship refueling failed")
    
    # Unlock a ship
    ship_name = "millennium_falcon"
    print(f"Unlocking {ship_name}...")
    unlock_success = ship_system.unlock_ship(ship_name)
    
    if unlock_success:
        print("✅ Ship unlocked successfully")
    else:
        print("❌ Ship unlocking failed")
    print()
    
    # Show ship travel statistics
    print("8. Ship Travel Statistics")
    print("-" * 25)
    
    stats = ship_system.get_travel_statistics()
    print(f"Total travels: {stats['total_travels']}")
    print(f"Successful travels: {stats['successful_travels']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print(f"Average travel time: {stats['average_travel_time']:.1f}s")
    
    if stats['recent_travels']:
        print("\nRecent travels:")
        for travel in stats['recent_travels'][-3:]:  # Last 3
            print(f"  - {travel.get('ship_name', 'Unknown')} to {travel.get('destination', 'Unknown')}")
            print(f"    Time: {travel.get('travel_time', 0)}s, Fuel: {travel.get('fuel_consumed', 0)}%")
    print()


def demonstrate_integration():
    """Demonstrate integration between terminal and ship travel."""
    if not TRAVEL_MODULES_AVAILABLE:
        print("Travel modules not available. Skipping integration demonstration.")
        return
    
    print("=== Travel System Integration ===\n")
    
    print("1. Combined Travel Strategy")
    print("-" * 28)
    
    # Check both terminal and ship availability
    terminal_system = get_terminal_travel_system()
    ship_system = get_ship_travel_system()
    
    # Scan for terminals
    print("Scanning for travel terminals...")
    terminal_results = terminal_system.scan_for_terminals()
    print(f"Found {len(terminal_results)} terminals")
    
    # Check ship availability
    print("Checking ship availability...")
    ship_availability = ship_system.check_ship_availability()
    print(f"Available ships: {ship_availability['total_available']}")
    
    # Determine best travel option
    if ship_availability['available_ships']:
        print("✅ Personal ship available - preferred option")
        best_ship = ship_availability['available_ships'][0]
        print(f"   Best ship: {best_ship['name']} ({best_ship['type']})")
        print(f"   Travel time: {best_ship['travel_time']}s")
    elif terminal_results:
        print("✅ Terminal available - fallback option")
        best_terminal = terminal_results[0]
        print(f"   Best terminal: {best_terminal.terminal_name} ({best_terminal.terminal_type.value})")
    else:
        print("❌ No travel options available")
    print()
    
    print("2. Travel Statistics Comparison")
    print("-" * 32)
    
    terminal_stats = terminal_system.get_travel_statistics()
    ship_stats = ship_system.get_travel_statistics()
    
    print("Terminal Travel:")
    print(f"  Success rate: {terminal_stats['success_rate']:.1f}%")
    print(f"  Total travels: {terminal_stats['total_travels']}")
    
    print("\nShip Travel:")
    print(f"  Success rate: {ship_stats['success_rate']:.1f}%")
    print(f"  Total travels: {ship_stats['total_travels']}")
    print(f"  Average travel time: {ship_stats['average_travel_time']:.1f}s")
    print()
    
    print("3. Travel Recommendations")
    print("-" * 26)
    
    if ship_availability['available_ships']:
        print("💡 Use personal ship for faster, more reliable travel")
        print("   - No waiting for shuttle schedules")
        print("   - Direct travel to destination")
        print("   - Lower cost for frequent travelers")
    elif terminal_results:
        print("💡 Use terminal travel as available option")
        print("   - Regular scheduled departures")
        print("   - Multiple destination options")
        print("   - Reliable service")
    else:
        print("⚠️  No travel options currently available")
        print("   - Check ship cooldowns")
        print("   - Look for nearby terminals")
        print("   - Consider alternative routes")


def demonstrate_data_files():
    """Demonstrate the data files for Batch 030."""
    print("=== Data Files Demonstration ===\n")
    
    # Check if data files exist
    starport_file = Path("data/starport_locations.yaml")
    shuttle_file = Path("data/shuttle_routes.yaml")
    
    print("1. Data File Status")
    print("-" * 20)
    print(f"Starport locations: {'✅ Found' if starport_file.exists() else '❌ Missing'}")
    print(f"Shuttle routes: {'✅ Found' if shuttle_file.exists() else '❌ Missing'}")
    print()
    
    if starport_file.exists():
        print("2. Starport Locations")
        print("-" * 22)
        
        try:
            import yaml
            with open(starport_file, 'r') as f:
                starport_data = yaml.safe_load(f)
            
            starports = starport_data.get('starports', {})
            total_starports = sum(len(planet_starports) for planet_starports in starports.values())
            
            print(f"Total starports: {total_starports}")
            print("\nStarports by planet:")
            
            for planet, planet_starports in starports.items():
                print(f"  {planet.title()}: {len(planet_starports)} starports")
                for starport_name, starport_info in planet_starports.items():
                    print(f"    - {starport_info['name']}")
                    destinations = len(starport_info.get('available_destinations', []))
                    print(f"      Destinations: {destinations}")
        except Exception as e:
            print(f"Error reading starport data: {e}")
        print()
    
    if shuttle_file.exists():
        print("3. Shuttle Routes")
        print("-" * 16)
        
        try:
            import yaml
            with open(shuttle_file, 'r') as f:
                shuttle_data = yaml.safe_load(f)
            
            routes = shuttle_data.get('shuttle_routes', {})
            total_routes = 0
            
            print("Shuttleports by planet:")
            for planet, planet_shuttleports in routes.items():
                print(f"  {planet.title()}: {len(planet_shuttleports)} shuttleports")
                for shuttleport_name, shuttleport_info in planet_shuttleports.items():
                    route_count = len(shuttleport_info.get('routes', []))
                    total_routes += route_count
                    print(f"    - {shuttleport_info['name']}: {route_count} routes")
            
            print(f"\nTotal routes: {total_routes}")
        except Exception as e:
            print(f"Error reading shuttle data: {e}")
        print()


def main():
    """Main demonstration function."""
    print("Batch 030 - Travel via Starports & Personal Ships")
    print("=" * 55)
    
    # Run demonstrations
    demonstrate_terminal_travel()
    demonstrate_ship_travel()
    demonstrate_integration()
    demonstrate_data_files()
    
    print("Demonstration completed successfully!")


if __name__ == "__main__":
    main() 