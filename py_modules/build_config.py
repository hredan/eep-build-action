import os
from py_modules.core_list import CoreList
from py_modules.esp32_info import Esp32Info
from py_modules.esp8266_info import Esp8266Info

class BuildConfig:
    def __init__(self):
        self.config = {}
        self.config["core"] = os.environ.get("INPUT_CORE")
        self.config["board"] = os.environ.get("INPUT_BOARD")
        self.config["sketch_name"] = os.environ.get("INPUT_SKETCH_NAME")
        self.config["build_path"] = f"./BIN_{self.config['core']}_{self.config['board']}"
        self.config["cpu_frequency"] = os.environ.get("INPUT_CPU_F")
        self.config["libs"] = os.environ.get("INPUT_LIBS")
        self.__add_core_version()
        if self.config["core"] == "esp32":
            self.__add_esp32_config()

    def __add_core_version(self):
        core_list = CoreList()
        core_version = core_list.get_core_version(self.config["core"])
        if not core_version:
            raise ValueError(f"Core '{self.config['core']}' not found in core list.")
        self.config["core_version"] = core_version
    
    def __add_esp32_config(self):
        esp_info = Esp32Info()
        self.config["mcu"] = esp_info.get_mcu_for_board(self.config["board"])
        self.config["bootloader_addr"] = esp_info.get_bootloader_address_for_mcu(self.config["mcu"])

    def get_config(self):
        return self.config
