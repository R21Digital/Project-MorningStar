import argparse
from data.importers.professions_importer import fetch_and_save


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch and store a profession from SWGR wiki")
    parser.add_argument("profession", help="Profession name, e.g. Architect")
    args = parser.parse_args(argv)
    path = fetch_and_save(args.profession)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()
