"""
Module for providing ESP32 board information including MCU and partition data.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""


import sys

from py_modules.info_base import InfoBase, CORE_DATA_DIR


class Esp32Info(InfoBase):
    """Provides ESP32 board information including MCU types and bootloader addresses."""

    def __init__(self):
        try:
            self.boards = self.load_json(f"{CORE_DATA_DIR}/esp32.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error loading ESP32 boards: {e}")

        try:
            partition_schemes = self.load_json(
                f"{CORE_DATA_DIR}/esp32_partition_schemes.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error loading ESP32 partition schemes: {e}")
            sys.exit(1)

        try:
            self.bootloader_addresses = self.load_json(
                f"{CORE_DATA_DIR}/esp32_mcu_bootloader_addr.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error loading ESP32 MCU bootloader addresses: {e}")
            sys.exit(1)

        super().__init__(partition_schemes)

    def get_mcu_for_board(self, board_name: str) -> str | None:
        """Return the MCU identifier for the given board name, or None if not found."""
        for board in self.boards:
            if board["board"] == board_name:
                return board["mcu"]
        return None

    def get_bootloader_address_for_mcu(self, mcu: str) -> str | None:
        """Return the bootloader flash address for the given MCU, or None if not found."""
        return self.bootloader_addresses.get(mcu, None)  # type: ignore[union-attr]

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
