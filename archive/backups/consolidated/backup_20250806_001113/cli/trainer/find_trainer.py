import argparse
from scripts.logic.trainer_navigator import navigate_to_trainer


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Navigate to a profession trainer")
    parser.add_argument("--trainer", required=True, help="Trainer profession name")
    parser.add_argument("--planet", default="tatooine", help="Planet name")
    parser.add_argument("--city", default="mos_eisley", help="City name")
    return parser.parse_args(argv)


def main(argv=None, agent=None):
    args = _parse_args(argv)
    return navigate_to_trainer(args.trainer, args.planet, args.city, agent)


if __name__ == "__main__":
    main()
