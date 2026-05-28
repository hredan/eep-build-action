"""
Tests for the BuildConfig module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json
import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from py_modules import build_config, core_list, esp32_info


def write_json(path: Any, data: Any) -> None:
    """Write data as JSON to the given path."""
    path.write_text(json.dumps(data), encoding="utf-8")


def test_build_config_initialization_with_env_vars(
    tmp_path: Any, monkeypatch: Any
) -> None:
    """Test that BuildConfig correctly initializes with environment variables."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "core_list.json",
        [{"core_name": "esp32", "latest_version": "3.0.0"}],
    )
    write_json(
        core_data_dir / "esp32.json",
        [{"name": "esp32dev", "board": "esp32dev", "mcu": "esp32"}],
    )
    write_json(core_data_dir / "esp32_partition_schemes.json", {})
    write_json(
        core_data_dir / "esp32_mcu_bootloader_addr.json",
        {"esp32": "0x1000"},
    )

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.setenv("INPUT_BOARD", "esp32dev")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "blink")
    monkeypatch.setenv("INPUT_CPU_F", "160")
    monkeypatch.setenv("INPUT_LIBS", "library1,library2")

    config = build_config.BuildConfig()

    assert config.core == "esp32"
    assert config.board == "esp32dev"
    assert config.sketch_name == "blink"
    assert config.cpu_f == "160"
    assert config.libs == "library1,library2"
    assert config.core_version == "3.0.0"
    assert config.build_path == "./BIN_esp32_esp32dev"


def test_build_config_get_mcu(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that BuildConfig correctly retrieves MCU for a board."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "core_list.json",
        [{"core_name": "esp32", "latest_version": "3.0.0"}],
    )
    write_json(
        core_data_dir / "esp32.json",
        [
            {"name": "esp32dev", "board": "esp32dev", "mcu": "esp32"},
            {"name": "esp32s3box", "board": "esp32s3box", "mcu": "esp32s3"},
        ],
    )
    write_json(core_data_dir / "esp32_partition_schemes.json", {})
    write_json(core_data_dir / "esp32_mcu_bootloader_addr.json", {})

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.setenv("INPUT_BOARD", "esp32dev")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "test")
    monkeypatch.delenv("INPUT_CPU_F", raising=False)
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    config = build_config.BuildConfig()

    assert config.get_mcu() == "esp32"


def test_build_config_get_bootloader_address(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that BuildConfig correctly retrieves bootloader address for an MCU."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "core_list.json",
        [{"core_name": "esp32", "latest_version": "3.0.0"}],
    )
    write_json(
        core_data_dir / "esp32.json",
        [{"name": "esp32dev", "board": "esp32dev", "mcu": "esp32"}],
    )
    write_json(core_data_dir / "esp32_partition_schemes.json", {})
    write_json(
        core_data_dir / "esp32_mcu_bootloader_addr.json",
        {"esp32": "0x1000", "esp32s3": "0x0"},
    )

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.setenv("INPUT_BOARD", "esp32dev")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "test")
    monkeypatch.delenv("INPUT_CPU_F", raising=False)
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    config = build_config.BuildConfig()

    assert config.get_bootloader_address() == "0x1000"


def test_build_config_missing_core_raises_error(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that BuildConfig raises error when core is not found."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "core_list.json",
        [{"core_name": "esp32", "latest_version": "3.0.0"}],
    )
    write_json(core_data_dir / "esp32.json", [])
    write_json(core_data_dir / "esp32_partition_schemes.json", {})
    write_json(core_data_dir / "esp32_mcu_bootloader_addr.json", {})

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setenv("INPUT_CORE", "unknown-core")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "test")
    monkeypatch.delenv("INPUT_CPU_F", raising=False)
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    with pytest.raises(ValueError, match="Core 'unknown-core' not found"):
        build_config.BuildConfig()


def test_build_config_get_mcu_returns_none_for_missing_board(
    tmp_path: Any, monkeypatch: Any
) -> None:
    """Test that get_mcu returns None when board is not configured."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()

    write_json(
        core_data_dir / "core_list.json",
        [{"core_name": "esp32", "latest_version": "3.0.0"}],
    )
    write_json(core_data_dir / "esp32.json", [])
    write_json(core_data_dir / "esp32_partition_schemes.json", {})
    write_json(core_data_dir / "esp32_mcu_bootloader_addr.json", {})

    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.delenv("INPUT_BOARD", raising=False)
    monkeypatch.setenv("INPUT_SKETCH_NAME", "test")
    monkeypatch.delenv("INPUT_CPU_F", raising=False)
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    config = build_config.BuildConfig()

    assert config.get_mcu() is None
