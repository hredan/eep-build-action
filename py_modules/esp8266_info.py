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
            self.partitions = self.load_json(
                f"{CORE_DATA_DIR}/esp8266_partition_schemes.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error initializing Esp8266Info: {e}")
            sys.exit(1)

    def get_mcu_for_board(self, board_name: str) -> str | None:
        """Return the MCU identifier for the given board name, or None if not found."""
        for board in self.boards:
            if board["name"] == board_name:
                return board["mcu"]
        return None

    def _get_partition_scheme(self, scheme_name: str) -> list[dict[str, str]]:
        """Return the partition scheme for the given scheme name, or an empty list if not found."""
        scheme = self.partitions.get(f"eagle.flash.{scheme_name.lower()}")
        if scheme is None:
            print(
                f"Error: Partition scheme '{scheme_name}' not found in esp8266_partition_schemes.json")
            sys.exit(1)
        return scheme

    def _get_spiffs_partition(self, scheme: list[dict[str, str]]) -> dict[str, str]:
        """Return the SPIFFS partition for the given partition scheme name, or None if not found."""
        for partition in scheme:
            if partition["name"] == "spiffs":
                return partition
        print(
            f"Error: SPIFFS partition not found in partition scheme '{scheme}'")
        sys.exit(1)

    def get_spiffs_start(self, scheme_name: str) -> str | None:
        """Return the SPIFFS start address for the given partition scheme name, or None if not found."""
        partitions = self._get_partition_scheme(scheme_name)
        spiffs_partition = self._get_spiffs_partition(partitions)
        return spiffs_partition.get("offset")

    def get_spiffs_size(self, scheme_name: str) -> str:
        """Return the SPIFFS size for the given partition scheme name, or None if not found."""
        partitions = self._get_partition_scheme(scheme_name)
        spiffs_partition = self._get_spiffs_partition(partitions)
        return spiffs_partition.get("size", "")
