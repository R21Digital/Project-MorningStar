import argparse
from utils.get_trainer_location import get_trainer_location


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Locate trainer coordinates")
    parser.add_argument("profession", help="Profession to search for")
    parser.add_argument("--planet", default="tatooine", help="Planet name")
    parser.add_argument("--city", default="mos_eisley", help="City name")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    result = get_trainer_location(args.profession, args.planet, args.city)
    if result:
        name, x, y = result
        print(f"{name} at ({x}, {y}) in {args.city.title()}, {args.planet.title()}")
        return result
    else:
        print(
            f"No trainer found for {args.profession} in {args.city}, {args.planet}."
        )
        print("Check trainers.json for available locations.")
        return None


if __name__ == "__main__":
    main()
