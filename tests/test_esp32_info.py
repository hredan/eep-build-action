"""
Tests for the Esp32Info module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json

from py_modules import esp32_info


def write_json(path, data):
    """Write data as JSON to the given path."""
    path.write_text(json.dumps(data), encoding="utf-8")


def test_esp32_info_loads_board_and_bootloader_data(tmp_path, monkeypatch):
    """Test that Esp32Info correctly loads board and bootloader address data."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "esp32.json",
        [
            {"name": "esp32dev", "board": "esp32dev", "mcu": "esp32"},
            {"name": "esp32s3box", "board": "esp32s3box", "mcu": "esp32s3"},
            {
                "name": "Nologo ESP32C3 Super Mini",
                "variant": "nologo_esp32c3_super_mini",
                "mcu": "esp32c3",
                "flash_size": [
                    "4MB"
                ],
                "led_builtin": "8",
                "board": "nologo_esp32c3_super_mini"
            },
        ],
    )
    write_json(
        core_data_dir / "esp32_partition_schemes.json",
        {"default": "Default 4MB with spiffs"},
    )
    write_json(
        core_data_dir / "esp32_mcu_bootloader_addr.json",
        {"esp32": "0x1000", "esp32s3": "0x0"},
    )

    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))

    info = esp32_info.Esp32Info()

    assert info.get_mcu_for_board("nologo_esp32c3_super_mini") == "esp32c3"
    assert info.get_mcu_for_board("esp32s3box") == "esp32s3"
    assert info.get_bootloader_address_for_mcu("esp32") == "0x1000"
    assert info.get_bootloader_address_for_mcu("esp32s3") == "0x0"


def test_esp32_info_returns_none_for_unknown_entries(tmp_path, monkeypatch):
    """Test that Esp32Info returns None for unknown board and MCU entries."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "esp32.json",
        [{"name": "esp32c3mini", "board": "esp32c3mini", "mcu": "esp32c3"}],
    )
    write_json(core_data_dir / "esp32_partition_schemes.json", {})
    write_json(
        core_data_dir / "esp32_mcu_bootloader_addr.json",
        {"esp32c3": "0x0"},
    )

    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))

    info = esp32_info.Esp32Info()

    assert info.get_mcu_for_board("missing-board") is None
    assert info.get_bootloader_address_for_mcu("missing-mcu") is None
