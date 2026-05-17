import requests
import os
import subprocess
import threading

def download_file(url, save_path):
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
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def download_json_files():
    urls = [
        "https://raw.githubusercontent.com/hredan/esp-board-overview/refs/heads/main/web-app/data/esp32.json",
        "https://raw.githubusercontent.com/hredan/esp-board-overview/refs/heads/main/web-app/data/esp32_partition_schemes.json",
        "https://raw.githubusercontent.com/hredan/esp-board-overview/refs/heads/main/web-app/data/esp32_mcu_bootloader_addr.json"
    ]
    
    for url in urls:
        filename = os.path.basename(url)
        save_path = os.path.join("./esp_core_info", filename)
        if not os.path.exists(save_path):
            download_file(url, save_path)


def run_bash_command(command, cwd=None, timeout=120, stream_output=False):
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

        process = subprocess.Popen(
            ["bash", "-lc", command],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        stdout_lines = []
        stderr_lines = []

        def stream(pipe, collected, prefix):
            for line in iter(pipe.readline, ""):
                collected.append(line)
                print(f"{prefix}{line}", end="", flush=True)
            pipe.close()

        stdout_thread = threading.Thread(target=stream, args=(process.stdout, stdout_lines, ""))
        stderr_thread = threading.Thread(target=stream, args=(process.stderr, stderr_lines, ""))
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
    except Exception as e:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Unexpected error while running command: {e}",
        }

def download_arduino_cli(version):
    url = f"https://downloads.arduino.cc/arduino-cli/arduino-cli_{version}_Linux_64bit.tar.gz"
    save_path = os.path.join("./tools", f"arduino-cli_{version}_Linux_64bit.tar.gz")
    if not os.path.exists(save_path):
        download_file(url, save_path)

def install_libs(libs):
    if libs:
        for lib in libs.split(","):
            lib = lib.strip()
            if lib:
                print(f"Installing library: {lib}")
                result = run_bash_command(f"./tools/arduino-cli lib install {lib}", stream_output=True)
                if not result["success"]:
                    print(f"Error installing library {lib}:\n{result['stderr']}")
                    exit(1)

def install_core(core, version=None):
    if version:
        core = f"{core}:{core}@{version}"
    else:
        core = f"{core}:{core}"
    print(f"Installing core: {core} version {version}")
    CORE_URL="https://espressif.github.io/arduino-esp32/package_esp32_index.json"
    result = run_bash_command(f"./tools/arduino-cli core update-index --additional-urls {CORE_URL}", stream_output=True)
    if not result["success"]:
        print(f"Error updating core index:\n{result['stderr']}")
        exit(1)

    result = run_bash_command(f"./tools/arduino-cli core install {core}", stream_output=True)
    if not result["success"]:
        print(f"Error installing core {core} version {version}:\n{result['stderr']}")
        exit(1)

def compile_sketch(sketch_name, build_path,fqbn, cpu_freq=None):
    command = f"./tools/arduino-cli compile --fqbn {fqbn} {sketch_name}.ino"
    if cpu_freq:
        command += f" --build-property cpu_freq={cpu_freq}"
    command += f" --build-path {build_path}"
    result = run_bash_command(command, stream_output=True)
    if not result["success"]:
        print(f"Error compiling sketch:\n{result['stderr']}")
        exit(1)
