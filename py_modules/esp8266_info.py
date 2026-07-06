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
        try:
            partitions = self.load_json(
                f"{CORE_DATA_DIR}/esp8266_partition_schemes.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error initializing Esp8266Info: {e}")
            sys.exit(1)
        super().__init__(partitions)

    def get_mcu_for_board(self, board_name: str) -> str | None:
        """Return the MCU identifier for the given board name, or None if not found."""
        for board in self.boards:
            if board["name"] == board_name:
                return board["mcu"]
        return None

    def get_spiffs_start(self, scheme_name: str) -> str | None:
        """Return the SPIFFS start address for the given partition scheme name, or None if not found."""
        scheme_name = f"eagle.flash.{scheme_name.lower()}"
        partitions = self._get_partition_scheme(scheme_name)
        spiffs_partition = self._get_spiffs_partition(partitions)
        return spiffs_partition.get("offset")

    def get_spiffs_size(self, scheme_name: str) -> str:
        """Return the SPIFFS size for the given partition scheme name, or None if not found."""
        scheme_name = f"eagle.flash.{scheme_name.lower()}"
        partitions = self._get_partition_scheme(scheme_name)
        spiffs_partition = self._get_spiffs_partition(partitions)
        return spiffs_partition.get("size", "")
