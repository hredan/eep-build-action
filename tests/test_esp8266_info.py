"""
Tests for the Esp8266Info module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json
from typing import Any

from py_modules import esp8266_info


def write_json(path: Any, data: Any) -> None:
    """Write data as JSON to the given path."""
    path.write_text(json.dumps(data), encoding="utf-8")


def test_esp8266_info_loads_board_data(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that Esp8266Info correctly loads board data from JSON."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "esp8266.json",
        [
            {"name": "nodemcu", "mcu": "esp8266"},
            {"name": "wemos_d1_mini", "mcu": "esp8266"},
            {"name": "generic", "mcu": "esp8266"},
        ],
    )

    monkeypatch.setattr(esp8266_info, "CORE_DATA_DIR", str(core_data_dir))

    info = esp8266_info.Esp8266Info()

    assert info.get_mcu_for_board("nodemcu") == "esp8266"
    assert info.get_mcu_for_board("wemos_d1_mini") == "esp8266"
    assert info.get_mcu_for_board("generic") == "esp8266"


def test_esp8266_info_returns_none_for_unknown_board(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that Esp8266Info returns None for unknown board names."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "esp8266.json",
        [
            {"name": "nodemcu", "mcu": "esp8266"},
        ],
    )

    monkeypatch.setattr(esp8266_info, "CORE_DATA_DIR", str(core_data_dir))

    info = esp8266_info.Esp8266Info()

    assert info.get_mcu_for_board("unknown-board") is None
    assert info.get_mcu_for_board("wemos_d1_mini") is None


def test_esp8266_info_handles_empty_board_list(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that Esp8266Info handles an empty board list correctly."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(core_data_dir / "esp8266.json", [])

    monkeypatch.setattr(esp8266_info, "CORE_DATA_DIR", str(core_data_dir))

    info = esp8266_info.Esp8266Info()

    assert info.get_mcu_for_board("nodemcu") is None
