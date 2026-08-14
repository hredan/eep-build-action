"""Tests for the create_eep_package module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest


SCRIPT_PATH = str(Path(__file__).parent.parent / "create_eep_package.py")


def _run_script(monkeypatch: Any, tmp_path: Path, *args: str) -> SystemExit:
    """Execute the script with given args and return the SystemExit."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [SCRIPT_PATH, *args])
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(SCRIPT_PATH, run_name="__main__")
    return exc_info.value


def test_create_eep_package_creates_archive(tmp_path: Path, monkeypatch: Any) -> None:
    """The script should create a flat .eep archive from ./EEP files."""
    eep_dir = tmp_path / "EEP"
    eep_dir.mkdir()
    (eep_dir / "firmware.bin").write_text("firmware")
    (eep_dir / "config.json").write_text("config")
    (eep_dir / "nested").mkdir()

    exit_info = _run_script(
        monkeypatch,
        tmp_path,
        "-c",
        "esp8266",
        "-b",
        "d1_mini",
        "-s",
        "MySketch",
    )

    assert exit_info.code == 0
    archive_path = tmp_path / "esp8266_d1_mini_MySketch.eep"
    assert archive_path.exists()

    with ZipFile(archive_path) as archive:
        assert sorted(archive.namelist()) == ["config.json", "firmware.bin"]


def test_create_eep_package_fails_without_required_args(
    tmp_path: Path,
    monkeypatch: Any,
    capsys: Any,
) -> None:
    """The script should fail when mandatory parameters are missing."""
    exit_info = _run_script(monkeypatch, tmp_path, "-c", "esp8266")

    assert exit_info.code == 1
    captured = capsys.readouterr()
    assert "ERROR: Sketch name ,Core or Board not defined" in captured.out
    assert "-s\tSketch" in captured.out


def test_create_eep_package_fails_when_eep_dir_is_missing(
    tmp_path: Path,
    monkeypatch: Any,
    capsys: Any,
) -> None:
    """The script should fail when the EEP directory is not present."""
    core_data_dir = tmp_path / "esp_core_info"
    core_data_dir.mkdir()
    (core_data_dir / "esp32.json").write_text("[]")
    (core_data_dir / "esp32_partition_schemes.json").write_text("{}")
    (core_data_dir / "esp32_mcu_bootloader_addr.json").write_text("{}")

    exit_info = _run_script(
        monkeypatch,
        tmp_path,
        "-c",
        "esp32",
        "-b",
        "esp32dev",
        "-s",
        "Blink",
    )

    assert exit_info.code == 1
    captured = capsys.readouterr()
    assert "Error could not find directory" in captured.out
