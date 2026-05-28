"""
Tests for the InfoBase module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json
from typing import Any

import pytest

from py_modules.info_base import InfoBase


def test_info_base_load_json_valid_file(tmp_path: Any) -> None:
    """Test that InfoBase can load a valid JSON file."""
    json_file = tmp_path / "test.json"
    test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
    json_file.write_text(json.dumps(test_data), encoding="utf-8")

    info_base = InfoBase()
    result = info_base.load_json(str(json_file))

    assert result == test_data


def test_info_base_load_json_invalid_file(tmp_path: Any) -> None:
    """Test that InfoBase exits when loading an invalid JSON file."""
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{invalid json content}", encoding="utf-8")

    info_base = InfoBase()
    with pytest.raises(SystemExit):
        info_base.load_json(str(json_file))


def test_info_base_load_json_missing_file() -> None:
    """Test that InfoBase exits when trying to load a non-existent file."""
    info_base = InfoBase()
    with pytest.raises(SystemExit):
        info_base.load_json("/nonexistent/path/file.json")


def test_info_base_load_json_complex_structure(tmp_path: Any) -> None:
    """Test that InfoBase can load complex nested JSON structures."""
    json_file = tmp_path / "complex.json"
    test_data = {
        "boards": [
            {"name": "board1", "mcu": "esp32", "details": {"flash": "4MB"}},
            {"name": "board2", "mcu": "esp8266", "details": {"flash": "2MB"}},
        ],
        "metadata": {"version": "1.0", "last_updated": "2026-05-28"}
    }
    json_file.write_text(json.dumps(test_data), encoding="utf-8")

    info_base = InfoBase()
    result = info_base.load_json(str(json_file))

    assert result == test_data
    assert result["boards"][0]["details"]["flash"] == "4MB"
