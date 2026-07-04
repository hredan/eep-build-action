"""
Module for managing build configuration based on environment variables.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import os
from py_modules.core_list import CoreList
from py_modules.esp32_info import Esp32Info


class BuildConfig:  # pylint: disable=too-many-instance-attributes
    """Holds the build configuration derived from environment variables."""

    def __init__(self):
        self.core = os.environ.get("INPUT_CORE")
        self.board = os.environ.get("INPUT_BOARD")
        self.sketch_name = os.environ.get("INPUT_SKETCH_NAME")
        self.build_path = f"./BIN_{self.core}_{self.board}"
        self.cpu_f = os.environ.get("INPUT_CPU_F")
        self.libs = os.environ.get("INPUT_LIBS")
        self.flash = os.environ.get("INPUT_FLASH")
        self.core_version = self.__get_core_version()
        self.__esp32_info = Esp32Info()

    def __get_core_version(self) -> str:
        core_list = CoreList()
        core_version = core_list.get_core_version(
            self.core) if self.core else None
        if not core_version:
            raise ValueError(f"Core '{self.core}' not found in core list.")
        return core_version

    def get_mcu(self) -> str | None:
        """Return the MCU identifier for the configured board."""
        return self.__esp32_info.get_mcu_for_board(self.board) if self.board else None

    def get_bootloader_address(self) -> str | None:
        """Return the bootloader flash address for the configured board's MCU."""
        mcu = self.get_mcu()
        return self.__esp32_info.get_bootloader_address_for_mcu(mcu) if mcu else None
