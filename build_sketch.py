import os
from py_modules import helper
from py_modules.esp32_info import Esp32Info

if __name__ == "__main__":
    print("Current Directory:", os.getcwd())
    helper.download_json_files()
    esp32_info = Esp32Info()

    # download and install Arduino CLI
    ARDUINO_CLI_VERSION="1.4.1"
    TOOL="./tools/arduino-cli"
    helper.download_arduino_cli(ARDUINO_CLI_VERSION)
    install_result = helper.run_bash_command(
        f"tar -xzf tools/arduino-cli_{ARDUINO_CLI_VERSION}_Linux_64bit.tar.gz -C tools/",
        stream_output=True,
    )
    if not install_result["success"]:
        print(f"Error installing Arduino CLI: {install_result['stderr']}")
        exit(1)
    if not os.path.exists(TOOL):
        print(f"Error: Arduino CLI not found at {TOOL}")
        exit(1)
    else:
        result = helper.run_bash_command(TOOL + " version", stream_output=True)
        if result["success"]:
            print(f"✅ Arduino CLI installed successfully")
        else:
            print(f"❌ Error verifying Arduino CLI installation:\n{result['stderr']}")
            exit(1)
    print(f"INPUT_SKETCH_NAME: {os.environ.get('INPUT_SKETCH_NAME')}")
    sketch_name = os.environ.get("INPUT_SKETCH_NAME")
    core = os.environ.get("INPUT_CORE")
    board = os.environ.get("INPUT_BOARD")
    core_version = os.environ.get("INPUT_CORE_VERSION")
    libs = os.environ.get("INPUT_LIBS")
    cpu_frequency = os.environ.get("INPUT_CPU_F")

    mcu = esp32_info.get_mcu_for_board(board)
    bootloader_addr = esp32_info.get_bootloader_address_for_mcu(mcu)

    helper.install_core(core, core_version)
    helper.install_libs(libs)

    FQBN_PARA=f"esp32:esp32:{board}:FlashFreq=80,PartitionScheme=default,UploadSpeed=921600"
    build_path = f"./BIN_{core}_{board}"
    helper.compile_sketch(sketch_name, build_path, FQBN_PARA, cpu_freq=cpu_frequency)

    