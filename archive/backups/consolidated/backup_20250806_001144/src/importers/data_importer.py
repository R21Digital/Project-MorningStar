import os
import json

DATA_DIR = "data"
METADATA_FILE = os.path.join(DATA_DIR, "metadata_index.json")


class DataImporter:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.metadata_path = METADATA_FILE
        self.metadata = self.load_metadata()

    def list_categories(self):
        return [
            name for name in os.listdir(self.data_dir)
            if os.path.isdir(os.path.join(self.data_dir, name))
        ]

    def load_metadata(self):
        if not os.path.exists(self.metadata_path):
            return {}
        with open(self.metadata_path, "r") as f:
            return json.load(f)

    def save_metadata(self):
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def update_metadata(self, category, data):
        self.metadata[category] = data
        self.save_metadata()


# Quick test
if __name__ == "__main__":
    importer = DataImporter()
    print("Available categories:", importer.list_categories())
