import json

from py_modules.info_base import InfoBase, CORE_DATA_DIR

class Esp32Info(InfoBase):
    def __init__(self):
        try:
            self.boards = self.load_json(f"{CORE_DATA_DIR}/esp32.json")
            self.partition_schemes = self.load_json(f"{CORE_DATA_DIR}/esp32_partition_schemes.json")
            self.bootloader_addresses = self.load_json(f"{CORE_DATA_DIR}/esp32_mcu_bootloader_addr.json")
        except Exception as e:
            print(f"Error initializing Esp32Info: {e}")
            exit(1)
    
    def get_mcu_for_board(self, board_name):
        for board in self.boards:
            if board["board"] == board_name:
                return board["mcu"]
        return None

    def get_bootloader_address_for_mcu(self, mcu):
        return self.bootloader_addresses.get(mcu, None)
