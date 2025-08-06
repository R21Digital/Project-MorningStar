from pathlib import Path
import cv2
import yaml

from src.vision.ocr import extract_text

SAMPLES_DIR = Path("docs/samples")
OUT_FILE = Path("data/trainers.yaml")


def _parse_info(text: str) -> dict:
    """Parse key-value pairs from OCR text."""
    info = {}
    for line in text.splitlines():
        if ':' in line:
            key, val = line.split(':', 1)
            info[key.strip().lower()] = val.strip()
    return info


def _load_existing() -> dict:
    if OUT_FILE.exists():
        with open(OUT_FILE, 'r') as fh:
            return yaml.safe_load(fh) or {}
    return {}


def _update(data: dict, info: dict) -> None:
    required = {'profession', 'planet', 'city', 'name', 'x', 'y'}
    if not required.issubset(info):
        return
    prof = info['profession'].lower()
    planet = info['planet'].lower()
    city = info['city'].lower()
    entry = {
        'name': info['name'],
        'x': int(info['x']),
        'y': int(info['y']),
    }
    data.setdefault(prof, {}).setdefault(planet, {})[city] = entry


def process_samples() -> None:
    if not SAMPLES_DIR.exists():
        print(f"No samples directory found at {SAMPLES_DIR}")
        return

    data = _load_existing()

    for img_path in sorted(SAMPLES_DIR.iterdir()):
        if img_path.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
            continue
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        text = extract_text(img)
        info = _parse_info(text)
        _update(data, info)

    with open(OUT_FILE, 'w') as fh:
        yaml.safe_dump(data, fh)


def main(argv=None):
    process_samples()


if __name__ == "__main__":
    main()
