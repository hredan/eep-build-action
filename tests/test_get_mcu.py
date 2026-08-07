"""
Tests for get_mcu.py.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import get_mcu
import runpy
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


GET_MCU_PATH = str(Path(__file__).parent.parent / "get_mcu.py")


def test_parse_args_reads_short_options(monkeypatch: Any) -> None:
    """Test argument parsing for -c, -b and -s options."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["get_mcu.py", "-c", "esp8266", "-b", "d1_mini"],
    )

    args = get_mcu.parse_args()

    assert args.core == "esp8266"
    assert args.board == "d1_mini"
    assert args.show_help is False


def test_parse_args_reads_help_flag(monkeypatch: Any) -> None:
    """Test argument parsing for help flag."""
    monkeypatch.setattr(sys, "argv", ["get_mcu.py", "-h"])

    args = get_mcu.parse_args()

    assert args.show_help is True


def test_print_help_outputs_expected_text(capsys: Any) -> None:
    """Test help text output for shell compatibility."""
    get_mcu.print_help()

    captured = capsys.readouterr()
    assert captured.out == get_mcu.HELP_TEXT


@pytest.mark.parametrize("core, board", [("", "d1_mini"), ("esp8266", ""), (None, "d1_mini"), ("esp8266", None)])
def test_get_mcu_exits_when_required_params_missing(core: Any, board: Any, capsys: Any) -> None:
    """Test validation for missing core or board parameters."""
    with pytest.raises(SystemExit) as exc_info:
        get_mcu.get_mcu(core, board)

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert "Error: core and board parameters are required." in captured.out


def test_get_mcu_returns_esp8266_for_non_esp32_core() -> None:
    """Test that all non-ESP32 cores resolve to esp8266."""
    mcu = get_mcu.get_mcu("esp8266", "d1_mini")

    assert mcu == "esp8266"


def test_get_mcu_esp32_uses_esp32_info_lookup() -> None:
    """Test ESP32 board lookup through Esp32Info provider."""
    with patch("get_mcu.Esp32Info") as mock_esp32_info_cls:
        mock_esp32_info = MagicMock()
        mock_esp32_info.get_mcu_for_board.return_value = "esp32c3"
        mock_esp32_info_cls.return_value = mock_esp32_info

        mcu = get_mcu.get_mcu("esp32", "esp32-c3-devkitm-1")

        assert mcu == "esp32c3"
        mock_esp32_info.get_mcu_for_board.assert_called_once_with(
            "esp32-c3-devkitm-1")


def test_get_mcu_esp32_board_not_found_exits(capsys: Any) -> None:
    """Test that missing ESP32 board exits with an error."""
    with patch("get_mcu.Esp32Info") as mock_esp32_info_cls:
        mock_esp32_info = MagicMock()
        mock_esp32_info.get_mcu_for_board.return_value = ""
        mock_esp32_info_cls.return_value = mock_esp32_info

        with pytest.raises(SystemExit) as exc_info:
            get_mcu.get_mcu("esp32", "unknown_board")

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert "Error: Board 'unknown_board' not found in ESP32 boards." in captured.out


def test_main_help_flag_prints_help_and_exits(monkeypatch: Any, capsys: Any) -> None:
    """Test CLI help path in __main__."""
    monkeypatch.setattr(sys, "argv", ["get_mcu.py", "-h"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(GET_MCU_PATH, run_name="__main__")

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert captured.out == get_mcu.HELP_TEXT


def test_main_prints_detected_mcu(monkeypatch: Any, capsys: Any) -> None:
    """Test CLI output for valid non-ESP32 invocation."""
    monkeypatch.setattr(
        sys, "argv", ["get_mcu.py", "-c", "esp8266", "-b", "d1_mini"])

    runpy.run_path(GET_MCU_PATH, run_name="__main__")

    captured = capsys.readouterr()
    assert captured.out.strip() == "esp8266"
