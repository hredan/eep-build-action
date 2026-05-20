import os
from py_modules.core_list import CoreList
from py_modules.esp32_info import Esp32Info
from py_modules.esp8266_info import Esp8266Info

class BuildConfig:
    def __init__(self):
        self.core = os.environ.get("INPUT_CORE")
        self.board = os.environ.get("INPUT_BOARD")
        self.sketch_name = os.environ.get("INPUT_SKETCH_NAME")
        self.build_path = f"./BIN_{self.core}_{self.board}"
        self.cpu_f = os.environ.get("INPUT_CPU_F")
        self.libs = os.environ.get("INPUT_LIBS")
        self.core_version = self.__get_core_version()
        self.__esp32_info = Esp32Info()

    def __get_core_version(self):
        core_list = CoreList()
        core_version = core_list.get_core_version(self.core)
        if not core_version:
            raise ValueError(f"Core '{self.core}' not found in core list.")
        return core_version
    
    def get_mcu(self):
        return self.__esp32_info.get_mcu_for_board(self.board)
    
    def get_bootloader_address(self):
        mcu = self.get_mcu()
        return self.__esp32_info.get_bootloader_address_for_mcu(mcu)
