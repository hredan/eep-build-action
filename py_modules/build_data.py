"""
This module contains functions to build the data partition for an Arduino sketch using the mklittlefs tool.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import os
import sys
from py_modules import helper

MKLITTLEFS_VERSION = "4.1.0"
MKLITTLEFS_HASH = "42acb97"
DATA_DIR = "./BIN_DATA"


def _find_mklittlefs_tool(core: str) -> str:
    user = os.environ.get('USER')
    arduino_tools_path = f"/home/{user}/.arduino15/packages/{core}/tools/mklittlefs/"
    if os.path.exists(arduino_tools_path):
        dir_entries = os.listdir(arduino_tools_path)
        if len(dir_entries) == 1:
            mklittlefs_path = os.path.join(
                arduino_tools_path, dir_entries[0], "mklittlefs")
            if os.path.exists(mklittlefs_path):
                return mklittlefs_path
            else:
                print(
                    f"Error: mklittlefs tool not found in {mklittlefs_path}.")
                sys.exit(1)
    else:
        print(
            f"Error: mklittlefs tool directory not found: {arduino_tools_path}.")
        sys.exit(1)
    return ""  # Return an empty string if the tool is not found


def build_data(core: str, spiffs_size: str, sketch_name: str) -> None:
    """
    Build the data partition for the given build configuration.
    """
    # _download_mklittlefs()
    mklittlefs_tool = _find_mklittlefs_tool(core)
    helper.run_bash_command(
        f"{mklittlefs_tool} --version", stream_output=True)
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    print("Building SPIFFS data partition for ESP8266...")
    mklittefs_path = f"{DATA_DIR}/{core}_{sketch_name}_littlefs.bin"
    if core == "esp8266":
        block = 8192
    else:
        block = 4096
    mklittefs_cmd = f"{mklittlefs_tool} -c ./data -p 256 -b {block} -s {int(spiffs_size, 16)} {mklittefs_path}"
    print(f"Running command: {mklittefs_cmd}")
    mklittlefs_result = helper.run_bash_command(
        mklittefs_cmd, stream_output=True)
    if not mklittlefs_result["success"]:
        print(
            f"Error building SPIFFS data partition:\n {mklittlefs_result['stderr']}")
        sys.exit(1)
    if not os.path.exists(mklittefs_path):
        print(f"Error: tool not found at {mklittefs_path}")
        sys.exit(1)
    else:
        print(f"✅ {mklittefs_path} built successfully")
