from py_modules.info_base import InfoBase, CORE_DATA_DIR

class Esp8266Info(InfoBase):
    def __init__(self):
        try:
            self.boards = self.load_json(f"{CORE_DATA_DIR}/esp8266.json")
        except Exception as e:
            print(f"Error initializing Esp8266Info: {e}")
            exit(1)
    
    def get_mcu_for_board(self, board_name):
        for board in self.boards:
            if board["name"] == board_name:
                return board["mcu"]
        return None