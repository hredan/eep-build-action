"""
Module providing the base class for board information loading.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import sys
import json
CORE_DATA_DIR = "esp_core_info"


class InfoBase:  # pylint: disable=too-few-public-methods
    """Base class providing JSON loading functionality for board information classes."""

    def __init__(self):
        pass

    def load_json(self, file_path):
        """Load and return parsed JSON data from the given file path."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error loading JSON from {file_path}: {e}")
            sys.exit(1)
