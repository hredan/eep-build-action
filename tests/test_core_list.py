"""
Tests for the CoreList module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json
from typing import Any

from py_modules import core_list


def write_json(path: Any, data: Any) -> None:
    """Write data as JSON to the given path."""
    path.write_text(json.dumps(data), encoding="utf-8")


def test_core_list_loads_core_data(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that CoreList correctly loads core data from JSON."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "core_list.json",
        [
            {"core_name": "esp32", "latest_version": "3.0.0"},
            {"core_name": "esp8266", "latest_version": "4.1.0"},
            {"core_name": "esp32s3", "latest_version": "2.0.1"},
        ],
    )

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))

    core_list_instance = core_list.CoreList()

    assert core_list_instance.get_core_version("esp32") == "3.0.0"
    assert core_list_instance.get_core_version("esp8266") == "4.1.0"
    assert core_list_instance.get_core_version("esp32s3") == "2.0.1"


def test_core_list_returns_none_for_unknown_core(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that CoreList returns None for unknown core names."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "core_list.json",
        [
            {"core_name": "esp32", "latest_version": "3.0.0"},
        ],
    )

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))

    core_list_instance = core_list.CoreList()

    assert core_list_instance.get_core_version("unknown-core") is None
    assert core_list_instance.get_core_version("esp8266") is None


def test_core_list_handles_empty_core_list(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that CoreList handles an empty core list correctly."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(core_data_dir / "core_list.json", [])

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))

    core_list_instance = core_list.CoreList()

    assert core_list_instance.get_core_version("esp32") is None
