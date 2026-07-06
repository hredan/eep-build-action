"""
Module providing helper functions for downloading files and running subprocesses.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import os
import sys
import subprocess
import threading
import shutil
from typing import IO
import requests
from py_modules.esp8266_info import Esp8266Info
from py_modules.build_config import BuildConfig

ARDUINO_CLI_TOOL = "./tools/arduino-cli"


def download_file(url: str, save_path: str) -> None:
    """
    Downloads a file from a URL and saves it locally.

    :param url: URL of the file
    :param save_path: Local save path (including file name)
    """
    try:
        # Use HTTP GET with streaming to avoid loading large files fully into memory
        with requests.get(url, stream=True, timeout=15) as response:
            response.raise_for_status()  # Raise an error if the HTTP status is not 200

            # Create the target directory if it does not exist yet
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Write the file in chunks
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Ignore empty chunks
                        file.write(chunk)

        print(f"✅ File saved successfully to: {save_path}")

    except requests.exceptions.MissingSchema:
        print("❌ Invalid URL. Please start with http:// or https://.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Please check your internet connection.")
    except requests.exceptions.Timeout:
        print("❌ Download timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Unexpected error: {e}")


def download_json_files() -> None:
    """Download all required ESP board JSON data files to the esp_core_info directory."""
    web_base_url = "https://raw.githubusercontent.com/hredan/esp-board-overview/refs/heads/main/web-app/data/"
    urls = [
        # core list
        web_base_url + "core_list.json"
    ]

    core = os.environ.get("INPUT_CORE")

    if core == "esp8266":
        urls.append(web_base_url + "esp8266.json")
        urls.append(web_base_url + "esp8266_partition_schemes.json")

    if core == "esp32":
        urls.append(web_base_url + "esp32.json")
        urls.append(web_base_url + "esp32_partition_schemes.json")
        urls.append(web_base_url + "esp32_mcu_bootloader_addr.json")

    for url in urls:
        filename = os.path.basename(url)
        save_path = os.path.join("./esp_core_info", filename)
        if not os.path.exists(save_path):
            download_file(url, save_path)


def run_bash_command(
    command: str,
    cwd: str | None = None,
    timeout: int = 120,
    stream_output: bool = False,
) -> dict[str, bool | int | str | None]:
    """
    Runs a command in bash and returns a structured result.

    :param command: Command string to execute
    :param cwd: Optional working directory
    :param timeout: Timeout in seconds
    :param stream_output: Print stdout/stderr as they are produced
    :return: dict with success, returncode, stdout, and stderr
    """
    try:
        if not stream_output:
            result = subprocess.run(
                ["bash", "-lc", command],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        process = subprocess.Popen(  # pylint: disable=consider-using-with
            ["bash", "-lc", command],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        def stream(pipe: IO[str], collected: list[str], prefix: str) -> None:
            """Read lines from a pipe and collect them, printing each with a prefix."""
            for line in iter(pipe.readline, ""):
                collected.append(line)
                print(f"{prefix}{line}", end="", flush=True)
            pipe.close()

        stdout_thread = threading.Thread(
            # type: ignore[arg-type]
            target=stream, args=(process.stdout, stdout_lines, ""))
        stderr_thread = threading.Thread(
            # type: ignore[arg-type]
            target=stream, args=(process.stderr, stderr_lines, ""))
        stdout_thread.start()
        stderr_thread.start()

        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout_thread.join()
            stderr_thread.join()
            return {
                "success": False,
                "returncode": None,
                "stdout": "".join(stdout_lines),
                "stderr": f"Command timed out after {timeout} seconds.",
            }

        stdout_thread.join()
        stderr_thread.join()

        return {
            "success": returncode == 0,
            "returncode": returncode,
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Unexpected error while running command: {e}",
        }


def unpack_tar_gz(archive_path: str, tool_name: str) -> None:
    """Unpack a .tar.gz archive to the specified directory."""
    if not os.path.exists(archive_path):
        print(f"❌ Archive not found: {archive_path}")
        sys.exit(1)

    unpack_result = run_bash_command(
        f"tar -xzf {archive_path} -C tools/",
        stream_output=True,
    )
    if not unpack_result["success"]:
        print(
            f"Error unpacking archive {archive_path}:\n {unpack_result['stderr']}")
        sys.exit(1)
    if not os.path.exists(tool_name):
        print(f"Error: tool not found at {tool_name}")
        sys.exit(1)
    else:
        print(f"✅ {tool_name} unpacked successfully")


def download_arduino_cli(version: str) -> None:
    """Download the arduino-cli binary for the given version if not already present."""
    archive_name = f"arduino-cli_{version}_Linux_64bit.tar.gz"
    save_path = os.path.join("./tools", archive_name)
    url = f"https://downloads.arduino.cc/arduino-cli/{archive_name}"
    if not os.path.exists(save_path):
        download_file(url, save_path)
        unpack_tar_gz(save_path, ARDUINO_CLI_TOOL)


def install_libs(libs: str | None) -> None:
    """Install a comma-separated list of Arduino libraries using arduino-cli."""
    if libs:
        for lib in libs.split(","):
            lib = lib.strip()
            if lib:
                print(f"Installing library: {lib}")
                result = run_bash_command(
                    f"./tools/arduino-cli lib install {lib}", stream_output=True)
                if not result["success"]:
                    print(
                        f"Error installing library {lib}:\n{result['stderr']}")
                    sys.exit(1)


def install_core(core: str, version: str | None = None) -> None:
    """Install the specified Arduino core with an optional version using arduino-cli."""
    if version:
        core = f"{core}:{core}@{version}"
    else:
        core = f"{core}:{core}"
    print(f"Installing core: {core} version {version}")
    if core == "esp32":
        core_url = "https://espressif.github.io/arduino-esp32/package_esp32_index.json"
    else:
        core_url = "https://arduino.esp8266.com/stable/package_esp8266com_index.json"
    # result = run_bash_command(
    #     f"{ARDUINO_CLI_TOOL} core update-index --additional-urls {core_url}", stream_output=True)
    # if not result["success"]:
    #     print(f"Error updating core index:\n{result['stderr']}")
    #     sys.exit(1)

    result = run_bash_command(
        f"{ARDUINO_CLI_TOOL} core install {core} --additional-urls {core_url}", stream_output=True)
    if not result["success"]:
        print(
            f"Error installing core {core} version {version}:\n{result['stderr']}")
        sys.exit(1)


def compile_sketch(sketch_name: str, build_path: str, fqbn: str, cpu_freq: str | None = None) -> None:
    """Compile an Arduino sketch using arduino-cli with the given FQBN and optional CPU frequency."""
    command = f"{ARDUINO_CLI_TOOL} compile --fqbn {fqbn} {sketch_name}.ino"
    if cpu_freq:
        command += f" --build-property cpu_freq={cpu_freq}"
    command += f" --build-path {build_path}"
    result = run_bash_command(command, stream_output=True, timeout=300)
    if not result["success"]:
        print(f"Error compiling sketch:\n{result['stderr']}")
        sys.exit(1)


def _create_eep_esp8266(
    config: BuildConfig,
    eep_dir: str,
    output_name: str,
    littlefs_src: str,
    has_littlefs: bool,
) -> None:
    """Create the EEP package files for an ESP8266 build."""
    app_src = os.path.join(config.build_path, f"{config.sketch_name}.ino.bin")
    app_dst_name = f"{config.core}_{output_name}.ino.bin"
    app_dst = os.path.join(eep_dir, app_dst_name)
    shutil.copy2(app_src, app_dst)

    eef_path = os.path.join(
        eep_dir, f"{config.core}_{config.board}_{config.sketch_name}.eef")
    command = ["--chip", "esp8266", "--baud",
               "460800", "write-flash", "0x0", app_dst_name]

    if has_littlefs:
        esp8266_info = Esp8266Info()
        spiffs_size = esp8266_info.get_spiffs_size(config.flash)
        littlefs_name = os.path.basename(littlefs_src)
        shutil.copy2(littlefs_src, os.path.join(eep_dir, littlefs_name))
        command.extend([f"{spiffs_size}", littlefs_name])

    with open(eef_path, "w", encoding="utf-8") as file:
        file.write('{\n\t"command": [')
        # type: ignore[arg-type]
        file.write(", ".join(f'"{item}"' for item in command))
        file.write("]\n}")


def _copy_esp32_binaries(config: BuildConfig, eep_dir: str, output_name: str) -> tuple[str, str, str]:
    """Copy ESP32 firmware binaries to the EEP directory and return their destination names."""
    app_dst_name = f"{config.core}_{output_name}.ino.bin"
    bootloader_dst_name = f"{config.core}_{output_name}.ino.bootloader.bin"
    partitions_dst_name = f"{config.core}_{output_name}.ino.partitions.bin"

    shutil.copy2(os.path.join(config.build_path, f"{config.sketch_name}.ino.bin"),
                 os.path.join(eep_dir, app_dst_name))
    shutil.copy2(os.path.join(config.build_path, f"{config.sketch_name}.ino.bootloader.bin"),
                 os.path.join(eep_dir, bootloader_dst_name))
    shutil.copy2(os.path.join(config.build_path, f"{config.sketch_name}.ino.partitions.bin"),
                 os.path.join(eep_dir, partitions_dst_name))

    boot_app_src = os.path.expanduser(
        f"~/.arduino15/packages/esp32/hardware/esp32/{config.core_version}/tools/partitions/boot_app0.bin"
    )
    if not os.path.exists(boot_app_src):
        raise FileNotFoundError(
            f"Missing required file for ESP32 EEP package: {boot_app_src}")
    shutil.copy2(boot_app_src, os.path.join(eep_dir, "boot_app0.bin"))

    return app_dst_name, bootloader_dst_name, partitions_dst_name


def _create_eep_esp32(
    config: BuildConfig,
    eep_dir: str,
    output_name: str,
    littlefs_src: str,
    has_littlefs: bool,
) -> None:
    """Create the EEP package files for an ESP32 build."""
    app_dst_name, bootloader_dst_name, partitions_dst_name = _copy_esp32_binaries(
        config, eep_dir, output_name)

    eef_path = os.path.join(eep_dir, f"{config.core}_{output_name}.eef")
    command = [
        "--chip", config.get_mcu(), "--baud", "921600",
        "--before", "default_reset", "--after", "hard_reset",
        "write-flash", "-z", "--flash_mode", "dio", "--flash_freq", "80m", "--flash_size", "detect",
        "0xe000", "boot_app0.bin",
        config.get_bootloader_address(), bootloader_dst_name,
        "0x10000", app_dst_name,
        "0x8000", partitions_dst_name,
    ]

    if has_littlefs:
        littlefs_name = os.path.basename(littlefs_src)
        shutil.copy2(littlefs_src, os.path.join(eep_dir, littlefs_name))
        command.extend(["0x290000", littlefs_name])

    with open(eef_path, "w", encoding="utf-8") as file:
        file.write('{\n\t"command": [')
        # type: ignore[arg-type]
        file.write(", ".join(f'"{item}"' for item in command))
        file.write("]\n}")


def create_eep_dir(config: BuildConfig) -> None:
    """Create the EEP package directory with firmware binaries and an .eef flash command file."""
    eep_dir = "./EEP"
    bin_data_dir = "./BIN_DATA"
    os.makedirs(eep_dir, exist_ok=True)

    for entry in os.listdir(eep_dir):
        entry_path = os.path.join(eep_dir, entry)
        if os.path.isdir(entry_path):
            shutil.rmtree(entry_path)
        else:
            os.remove(entry_path)

    output_name = f"{config.board}_{config.sketch_name}"
    littlefs_name = f"{config.core}_{config.sketch_name}_littlefs.bin"
    littlefs_src = os.path.join(bin_data_dir, littlefs_name)
    has_littlefs = os.path.exists(littlefs_src)

    if config.core == "esp8266":
        _create_eep_esp8266(config, eep_dir, output_name,
                            littlefs_src, has_littlefs)
    elif config.core == "esp32":
        _create_eep_esp32(config, eep_dir, output_name,
                          littlefs_src, has_littlefs)
    else:
        raise ValueError(
            f"Unsupported core for EEP package creation: {config.core}")

    readme_path = os.path.join(eep_dir, "readme.txt")
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as file:
            file.write(
                "This package can be used with ESPEasyFlasher2.0 "
                "(https://github.com/hredan/ESPEASYFLASHER_2.0)\n")
