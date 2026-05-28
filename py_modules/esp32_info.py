"""
Module for providing ESP32 board information including MCU and partition data.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""


from py_modules.info_base import InfoBase, CORE_DATA_DIR


class Esp32Info(InfoBase):
    """Provides ESP32 board information including MCU types and bootloader addresses."""

    def __init__(self):
        try:
            self.boards = self.load_json(f"{CORE_DATA_DIR}/esp32.json")
            self.partition_schemes = self.load_json(
                f"{CORE_DATA_DIR}/esp32_partition_schemes.json")
            self.bootloader_addresses = self.load_json(
                f"{CORE_DATA_DIR}/esp32_mcu_bootloader_addr.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error initializing Esp32Info: {e}")

    def get_mcu_for_board(self, board_name: str) -> str | None:
        """Return the MCU identifier for the given board name, or None if not found."""
        for board in self.boards:
            if board["board"] == board_name:
                return board["mcu"]
        return None

    def get_bootloader_address_for_mcu(self, mcu: str) -> str | None:
        """Return the bootloader flash address for the given MCU, or None if not found."""
        return self.bootloader_addresses.get(mcu, None)  # type: ignore[union-attr]
