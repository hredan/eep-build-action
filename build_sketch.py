"""
Main script for building an Arduino sketch using the configured core, board and scheme.

For confiuguration you can use the information on ESP Board Overview webpage:
https://hredan.github.io/esp-board-overview/

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import os
import sys
from py_modules import helper
from py_modules.build_config import BuildConfig

if __name__ == "__main__":
    print("Current Directory:", os.getcwd())
    helper.download_json_files()

    build_config = BuildConfig()

    # download and install Arduino CLI
    ARDUINO_CLI_VERSION = "1.4.1"
    TOOL = "./tools/arduino-cli"
    helper.download_arduino_cli(ARDUINO_CLI_VERSION)
    install_result = helper.run_bash_command(
        f"tar -xzf tools/arduino-cli_{ARDUINO_CLI_VERSION}_Linux_64bit.tar.gz -C tools/",
        stream_output=True,
    )
    if not install_result["success"]:
        print(f"Error installing Arduino CLI: {install_result['stderr']}")
        sys.exit(1)
    if not os.path.exists(TOOL):
        print(f"Error: Arduino CLI not found at {TOOL}")
        sys.exit(1)
    else:
        result = helper.run_bash_command(TOOL + " version", stream_output=True)
        if result["success"]:
            print("✅ Arduino CLI installed successfully")
        else:
            print(
                f"❌ Error verifying Arduino CLI installation:\n{result['stderr']}")
            sys.exit(1)

    helper.install_core(build_config.core or "", build_config.core_version)
    helper.install_libs(build_config.libs or "")

    FQBN_PARA = f"esp32:esp32:{build_config.board}:FlashFreq=80,PartitionScheme=default,UploadSpeed=921600"
    BUILD_PATH = f"./BIN_{build_config.core}_{build_config.board}"
    helper.compile_sketch(build_config.sketch_name or "",
                          BUILD_PATH, FQBN_PARA, cpu_freq=build_config.cpu_f)
    helper.create_eep_dir(build_config)
