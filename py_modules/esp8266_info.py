"""
Module for providing ESP8266 board information.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import sys


from py_modules.info_base import InfoBase, CORE_DATA_DIR


class Esp8266Info(InfoBase):
    """Provides ESP8266 board information loaded from JSON data files."""

    def __init__(self):
        try:
            self.boards = self.load_json(f"{CORE_DATA_DIR}/esp8266.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error initializing Esp8266Info: {e}")
            sys.exit(1)

    def get_mcu_for_board(self, board_name: str) -> str | None:
        """Return the MCU identifier for the given board name, or None if not found."""
        for board in self.boards:
            if board["name"] == board_name:
                return board["mcu"]
        return None
