"""
Tests for the build_sketch module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json
from typing import Any
from pathlib import Path
from unittest.mock import patch

import pytest

from py_modules import core_list, esp32_info

BUILD_SKETCH_PATH = str(Path(__file__).parent.parent / "build_sketch.py")


def _setup_tmp_core_data(tmp_path: Any) -> Path:
    """Create minimal esp_core_info JSON files in tmp_path and return the directory."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()
    partition_schemes = """
    {
        "default": [
            {
                "name": "spiffs",
                "type": "data",
                "subtype": "spiffs",
                "offset": "0x290000",
                "size": "0x160000"
            }
        ]
    }
"""
    {}
    (core_data_dir / "core_list.json").write_text(
        json.dumps([{"core_name": "esp32", "latest_version": "3.0.0"}])
    )
    (core_data_dir / "esp32.json").write_text(
        json.dumps([{"name": "esp32dev", "board": "esp32dev", "mcu": "esp32"}])
    )
    (core_data_dir / "esp32_partition_schemes.json").write_text(partition_schemes)
    (core_data_dir / "esp32_mcu_bootloader_addr.json").write_text(
        json.dumps({"esp32": "0x1000"})
    )
    return core_data_dir


def test_build_sketch_main_workflow(tmp_path: Any, monkeypatch: Any) -> None:
    """Test the main build_sketch workflow with mocked dependencies."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.setenv("INPUT_BOARD", "esp32dev")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "blink")
    monkeypatch.setenv("INPUT_CPU_F", "160")
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    core_data_dir = _setup_tmp_core_data(tmp_path)
    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))

    with patch("py_modules.helper.download_json_files"), \
            patch("py_modules.helper.download_arduino_cli"), \
            patch("py_modules.helper.install_core"), \
            patch("py_modules.helper.install_libs"), \
            patch("py_modules.helper.compile_sketch"), \
            patch("py_modules.helper.create_eep_dir"), \
            patch("py_modules.helper.run_bash_command") as mock_run, \
            patch("os.path.exists", return_value=True), \
            patch("py_modules.build_data._find_mklittlefs_tool", return_value="/path/to/mklittlefs"):

        mock_run.return_value = {"success": True}

        import runpy
        try:
            runpy.run_path(BUILD_SKETCH_PATH, run_name="__main__")
        except SystemExit:
            pass

        assert mock_run.call_count >= 1


def test_build_sketch_arduino_cli_extraction_failure(tmp_path: Any, monkeypatch: Any) -> None:
    """Test build_sketch handles Arduino CLI extraction failure."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.setenv("INPUT_BOARD", "esp32dev")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "blink")
    monkeypatch.delenv("INPUT_CPU_F", raising=False)
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    core_data_dir = _setup_tmp_core_data(tmp_path)
    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))

    with patch("py_modules.helper.download_json_files"), \
            patch("py_modules.helper.download_arduino_cli"), \
            patch("py_modules.helper.run_bash_command") as mock_run:

        mock_run.return_value = {
            "success": False, "stderr": "Extraction failed"}

        import runpy
        with pytest.raises(SystemExit):
            runpy.run_path(BUILD_SKETCH_PATH, run_name="__main__")


def test_build_sketch_arduino_cli_not_found(tmp_path: Any, monkeypatch: Any) -> None:
    """Test build_sketch handles missing Arduino CLI binary."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.setenv("INPUT_BOARD", "esp32dev")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "blink")
    monkeypatch.delenv("INPUT_CPU_F", raising=False)
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    core_data_dir = _setup_tmp_core_data(tmp_path)
    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))

    with patch("py_modules.helper.download_json_files"), \
            patch("py_modules.helper.download_arduino_cli"), \
            patch("py_modules.helper.run_bash_command") as mock_run, \
            patch("os.path.exists", return_value=False):

        mock_run.return_value = {"success": True}

        import runpy
        with pytest.raises(SystemExit):
            runpy.run_path(BUILD_SKETCH_PATH, run_name="__main__")


def test_build_sketch_prints_current_directory(tmp_path: Any, monkeypatch: Any, capsys: Any) -> None:
    """Test that build_sketch prints current directory at startup."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INPUT_CORE", "esp32")
    monkeypatch.setenv("INPUT_BOARD", "esp32dev")
    monkeypatch.setenv("INPUT_SKETCH_NAME", "blink")
    monkeypatch.delenv("INPUT_CPU_F", raising=False)
    monkeypatch.delenv("INPUT_LIBS", raising=False)

    core_data_dir = _setup_tmp_core_data(tmp_path)
    monkeypatch.setattr(core_list, "CORE_DATA_DIR", str(core_data_dir))
    monkeypatch.setattr(esp32_info, "CORE_DATA_DIR", str(core_data_dir))

    with patch("py_modules.helper.download_json_files"), \
            patch("py_modules.helper.download_arduino_cli"), \
            patch("py_modules.helper.install_core"), \
            patch("py_modules.helper.install_libs"), \
            patch("py_modules.helper.compile_sketch"), \
            patch("py_modules.helper.create_eep_dir"), \
            patch("py_modules.helper.run_bash_command") as mock_run, \
            patch("py_modules.build_data._find_mklittlefs_tool", return_value="/path/to/mklittlefs"), \
            patch("os.path.exists", return_value=True):

        mock_run.return_value = {"success": True}

        import runpy
        try:
            runpy.run_path(BUILD_SKETCH_PATH, run_name="__main__")
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "Current Directory:" in captured.out
