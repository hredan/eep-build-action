
import os
import sys
from py_modules import helper

MKLITTLEFS_VERSION = "4.1.0"
MKLITTLEFS_HASH = "42acb97"
MKLITTLEFS_TOOL = "./tools/mklittlefs/mklittlefs"

DATA_DIR = "./BIN_DATA"


def _download_mklittlefs():
    """
    Download the mklittlefs tool if it doesn't exist.
    """
    MKLITTLEFS_ARCHIVE_NAME = f"x86_64-linux-gnu-mklittlefs-{MKLITTLEFS_HASH}.tar.gz"
    MKLITTLEFS_TOOL_URL = f"https://github.com/earlephilhower/mklittlefs/releases/download/{MKLITTLEFS_VERSION}/{MKLITTLEFS_ARCHIVE_NAME}"
    if not os.path.exists(f"./tools/{MKLITTLEFS_ARCHIVE_NAME}"):
        print("Downloading mklittlefs tool...")
        helper.download_file(MKLITTLEFS_TOOL_URL,
                             f"./tools/{MKLITTLEFS_ARCHIVE_NAME}")
        helper.unpack_tar_gz(
            f"./tools/{MKLITTLEFS_ARCHIVE_NAME}", MKLITTLEFS_TOOL)


def build_data(core: str, spiffs_size: str, sketch_name: str) -> None:
    """
    Build the data partition for the given build configuration.
    """
    _download_mklittlefs()

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if core == "esp8266":
        print("Building SPIFFS data partition for ESP8266...")
        mklittefs_path = f"{DATA_DIR}/esp8266_{sketch_name}_littlefs.bin"
        mklittlefs_result = helper.run_bash_command(
            f"{MKLITTLEFS_TOOL} -c ./data -p 256 -b 8192 -s {spiffs_size} {mklittefs_path}")
        if not mklittlefs_result["success"]:
            print(
                f"Error building SPIFFS data partition:\n {mklittlefs_result['stderr']}")
            sys.exit(1)
        if not os.path.exists(mklittefs_path):
            print(f"Error: tool not found at {mklittefs_path}")
            sys.exit(1)
        else:
            print(f"✅ {mklittefs_path} unpacked successfully")
