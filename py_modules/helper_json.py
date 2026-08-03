"""
Helper functions for JSON operations.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json
import sys
from typing import Any


def load_json(file_path: str) -> Any:
    """Load and return parsed JSON data from the given file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error loading JSON from {file_path}: {e}")
        sys.exit(1)
