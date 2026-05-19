import os
from py_modules import helper
from py_modules.build_config import BuildConfig

if __name__ == "__main__":
    print("Current Directory:", os.getcwd())
    helper.download_json_files()

    build_config = BuildConfig()
    config = build_config.get_config()

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


    helper.install_core(config["core"], config["core_version"])
    helper.install_libs(config["libs"])

    FQBN_PARA=f"esp32:esp32:{config["board"]}:FlashFreq=80,PartitionScheme=default,UploadSpeed=921600"
    build_path = f"./BIN_{config["core"]}_{config["board"]}"
    helper.compile_sketch(config["sketch_name"], build_path, FQBN_PARA, cpu_freq=config["cpu_frequency"])
    helper.create_eep_dir(config)
