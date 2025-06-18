import argparse


def craft_bandage(quantity: int) -> str:
    """Return a message after crafting bandages."""
    return f"Crafted {quantity} bandage{'s' if quantity != 1 else ''}"


def main(argv=None) -> str:
    """Entry point for the Medic crafting CLI."""
    parser = argparse.ArgumentParser(description="Medic crafting utility")
    parser.add_argument("action", choices=["bandage"], help="Item to craft")
    parser.add_argument("-q", "--quantity", type=int, default=1, help="Number of items to craft")
    args = parser.parse_args(argv)

    if args.action == "bandage":
        message = craft_bandage(args.quantity)
        print(message)
        return message
    return ""


if __name__ == "__main__":
    main()
