from py_modules import helper
from py_modules.esp32_info import Esp32Info

if __name__ == "__main__":
    helper.download_json_files()
    esp32_info = Esp32Info()