"""
Travel Locations and Terminals

This module defines the data structures for travel locations and terminals
used in the planetary travel system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional


class TerminalType(Enum):
    """Types of travel terminals."""
    SHUTTLEPORT = "shuttleport"
    STARPORT = "starport"
    SHIP = "ship"
    UNKNOWN = "unknown"


@dataclass
class TravelLocation:
    """Represents a travel location."""
    city: str
    planet: str
    coordinates: Tuple[int, int]
    zone: str = "unknown"
    description: str = ""


@dataclass
class TravelTerminal:
    """Represents a travel terminal."""
    name: str
    city: str
    planet: str
    terminal_type: TerminalType
    coordinates: Tuple[int, int]
    npc: str = ""
    description: str = ""
    available_destinations: Optional[list] = None


# Known travel locations
KNOWN_LOCATIONS = {
    "mos_eisley": TravelLocation(
        city="mos_eisley",
        planet="tatooine",
        coordinates=(3520, -4800),
        zone="city",
        description="Spaceport city on Tatooine"
    ),
    "theed": TravelLocation(
        city="theed",
        planet="naboo",
        coordinates=(5000, -4000),
        zone="city",
        description="Capital city of Naboo"
    ),
    "coronet": TravelLocation(
        city="coronet",
        planet="corellia",
        coordinates=(123, 456),
        zone="city",
        description="Major city on Corellia"
    ),
    "tyrena": TravelLocation(
        city="tyrena",
        planet="corellia",
        coordinates=(200, 300),
        zone="city",
        description="City on Corellia"
    ),
    "bestine": TravelLocation(
        city="bestine",
        planet="tatooine",
        coordinates=(4000, -6000),
        zone="city",
        description="City on Tatooine"
    ),
    "kaadara": TravelLocation(
        city="kaadara",
        planet="naboo",
        coordinates=(6000, -3000),
        zone="city",
        description="City on Naboo"
    ),
    "khoonda": TravelLocation(
        city="khoonda",
        planet="dantooine",
        coordinates=(100, 200),
        zone="city",
        description="Settlement on Dantooine"
    )
}


# Known travel terminals
KNOWN_TERMINALS = {
    "mos_eisley_shuttleport": TravelTerminal(
        name="Mos Eisley Shuttleport",
        city="mos_eisley",
        planet="tatooine",
        terminal_type=TerminalType.SHUTTLEPORT,
        coordinates=(3520, -4800),
        npc="Shuttle Conductor",
        description="Shuttleport in Mos Eisley",
        available_destinations=[
            {"planet": "corellia", "city": "coronet"},
            {"planet": "naboo", "city": "theed"},
            {"planet": "dantooine", "city": "khoonda"}
        ]
    ),
    "theed_starport": TravelTerminal(
        name="Theed Starport",
        city="theed",
        planet="naboo",
        terminal_type=TerminalType.STARPORT,
        coordinates=(5000, -4000),
        npc="Starport Attendant",
        description="Starport in Theed",
        available_destinations=[
            {"planet": "tatooine", "city": "mos_eisley"},
            {"planet": "corellia", "city": "coronet"},
            {"planet": "dantooine", "city": "khoonda"}
        ]
    ),
    "coronet_shuttleport": TravelTerminal(
        name="Coronet Shuttleport",
        city="coronet",
        planet="corellia",
        terminal_type=TerminalType.SHUTTLEPORT,
        coordinates=(123, 456),
        npc="Shuttle Conductor",
        description="Shuttleport in Coronet",
        available_destinations=[
            {"planet": "tatooine", "city": "mos_eisley"},
            {"planet": "naboo", "city": "theed"},
            {"planet": "corellia", "city": "tyrena"}
        ]
    ),
    "tyrena_shuttleport": TravelTerminal(
        name="Tyrena Shuttleport",
        city="tyrena",
        planet="corellia",
        terminal_type=TerminalType.SHUTTLEPORT,
        coordinates=(200, 300),
        npc="Shuttle Conductor",
        description="Shuttleport in Tyrena",
        available_destinations=[
            {"planet": "corellia", "city": "coronet"},
            {"planet": "naboo", "city": "moenia"}
        ]
    ),
    "bestine_shuttleport": TravelTerminal(
        name="Bestine Shuttleport",
        city="bestine",
        planet="tatooine",
        terminal_type=TerminalType.SHUTTLEPORT,
        coordinates=(4000, -6000),
        npc="Shuttle Conductor",
        description="Shuttleport in Bestine",
        available_destinations=[
            {"planet": "tatooine", "city": "mos_eisley"},
            {"planet": "tatooine", "city": "anchorhead"}
        ]
    ),
    "kaadara_starport": TravelTerminal(
        name="Kaadara Starport",
        city="kaadara",
        planet="naboo",
        terminal_type=TerminalType.STARPORT,
        coordinates=(6000, -3000),
        npc="Starport Attendant",
        description="Starport in Kaadara",
        available_destinations=[
            {"planet": "naboo", "city": "theed"},
            {"planet": "corellia", "city": "tyrena"}
        ]
    ),
    "khoonda_shuttleport": TravelTerminal(
        name="Khoonda Shuttleport",
        city="khoonda",
        planet="dantooine",
        terminal_type=TerminalType.SHUTTLEPORT,
        coordinates=(100, 200),
        npc="Shuttle Conductor",
        description="Shuttleport in Khoonda",
        available_destinations=[
            {"planet": "tatooine", "city": "mos_eisley"},
            {"planet": "naboo", "city": "theed"}
        ]
    )
}


def get_location(city: str, planet: str) -> Optional[TravelLocation]:
    """Get a known travel location.
    
    Parameters
    ----------
    city : str
        City name
    planet : str
        Planet name
        
    Returns
    -------
    Optional[TravelLocation]
        Travel location if found, None otherwise
    """
    key = f"{city}_{planet}"
    for location in KNOWN_LOCATIONS.values():
        if location.city == city and location.planet == planet:
            return location
    return None


def get_terminal(terminal_name: str) -> Optional[TravelTerminal]:
    """Get a known travel terminal.
    
    Parameters
    ----------
    terminal_name : str
        Terminal name
        
    Returns
    -------
    Optional[TravelTerminal]
        Travel terminal if found, None otherwise
    """
    return KNOWN_TERMINALS.get(terminal_name)


def get_terminals_by_planet(planet: str) -> list:
    """Get all terminals on a specific planet.
    
    Parameters
    ----------
    planet : str
        Planet name
        
    Returns
    -------
    list
        List of terminals on the planet
    """
    terminals = []
    for terminal in KNOWN_TERMINALS.values():
        if terminal.planet == planet:
            terminals.append(terminal)
    return terminals


def get_terminals_by_type(terminal_type: TerminalType) -> list:
    """Get all terminals of a specific type.
    
    Parameters
    ----------
    terminal_type : TerminalType
        Type of terminal
        
    Returns
    -------
    list
        List of terminals of the specified type
    """
    terminals = []
    for terminal in KNOWN_TERMINALS.values():
        if terminal.terminal_type == terminal_type:
            terminals.append(terminal)
    return terminals


def find_nearest_terminal(location: TravelLocation, terminal_type: TerminalType = None) -> Optional[TravelTerminal]:
    """Find the nearest terminal to a location.
    
    Parameters
    ----------
    location : TravelLocation
        Current location
    terminal_type : TerminalType, optional
        Preferred terminal type
        
    Returns
    -------
    Optional[TravelTerminal]
        Nearest terminal, or None if not found
    """
    nearest_terminal = None
    min_distance = float('inf')
    
    for terminal in KNOWN_TERMINALS.values():
        if terminal_type and terminal.terminal_type != terminal_type:
            continue
            
        distance = _calculate_distance(location.coordinates, terminal.coordinates)
        if distance < min_distance:
            min_distance = distance
            nearest_terminal = terminal
    
    return nearest_terminal


def _calculate_distance(coords1: Tuple[int, int], coords2: Tuple[int, int]) -> float:
    """Calculate distance between two coordinate pairs."""
    x1, y1 = coords1
    x2, y2 = coords2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 