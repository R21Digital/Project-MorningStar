def execute_movement(step: dict) -> None:
    """Simulate a movement step by logging the destination.

    The ``step`` dictionary should contain a ``to`` mapping with ``planet`` and
    ``city`` keys. Only a simple print statement is used to emulate movement.
    """

    destination = step.get("to", {})
    planet = destination.get("planet", "Unknown planet")
    city = destination.get("city", "Unknown city")

    print(f"Moving to {planet}, {city}")
