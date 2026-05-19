import json
CORE_DATA_DIR = "esp_core_info"

class InfoBase:
    def __init__(self):
        pass

    def load_json(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {file_path}: {e}")
            exit(1)