"""
Main script for building an Arduino sketch using the configured core, board and scheme.

For confiuguration you can use the information on ESP Board Overview webpage:
https://hredan.github.io/esp-board-overview/

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import os
from py_modules import helper
from py_modules import build_data
from py_modules.esp32_info import Esp32Info
from py_modules.esp8266_info import Esp8266Info
from py_modules.build_config import BuildConfig

if __name__ == "__main__":
    print("Current Directory:", os.getcwd())

    helper.download_json_files()

    build_config = BuildConfig()

    # download and install Arduino CLI
    ARDUINO_CLI_VERSION = "1.4.1"
    helper.download_arduino_cli(ARDUINO_CLI_VERSION)

    helper.install_core(build_config.core or "", build_config.core_version)
    helper.install_libs(build_config.libs or "")

    fqbn_para = ""
    if build_config.core == "esp32":
        fqbn_para = f"esp32:esp32:{build_config.board}:PartitionScheme={build_config.flash}"
    else:
        fqbn_para = f"esp8266:esp8266:{build_config.board}:xtal={build_config.cpu_f}" + \
            ",vt=flash,exception=disabled,stacksmash=disabled,ssl=all,mmu=3232,non32xfer=fast" + \
            f",eesz={build_config.flash},ip=hb2f,dbg=Disabled,lvl=None____,wipe=none,baud=921600"
    BUILD_PATH = f"./BIN_{build_config.core}_{build_config.board}"
    print(
        f"Building sketch: {build_config.sketch_name} " +
        f"for board: {build_config.board} with core: {build_config.core}"
    )
    helper.compile_sketch(build_config.sketch_name or "",
                          BUILD_PATH, fqbn_para, cpu_freq=build_config.cpu_f)
    if os.path.exists("data"):
        print("Building data partition...")
        core = build_config.core
        if core == "esp8266":
            esp8266_info = Esp8266Info()
            spiffs_size = esp8266_info.get_spiffs_size(build_config.flash)
        else:
            esp32_info = Esp32Info()
            spiffs_size = esp32_info.get_spiffs_size(build_config.flash)
        build_data.build_data(
            build_config.core, spiffs_size, build_config.sketch_name)
    helper.create_eep_dir(build_config)
