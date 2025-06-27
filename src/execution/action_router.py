"""Dispatch low-level action handlers."""

from utils.movement_manager import travel_to
from utils.npc_handler import interact_with_npc
from utils.combat_handler import engage_targets

ACTION_ROUTER = {
    "combat": engage_targets,
    "move": travel_to,
    "npc": interact_with_npc,
}


def get_handler(action_type: str):
    """Return the handler function for ``action_type`` or ``None``."""
    return ACTION_ROUTER.get(action_type)
