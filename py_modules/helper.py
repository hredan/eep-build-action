import requests
import os
import subprocess

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
        "https://raw.githubusercontent.com/hredan/esp-board-overview/refs/heads/main/web-app/data/esp32_partitions.json",
        "https://raw.githubusercontent.com/hredan/esp-board-overview/refs/heads/main/web-app/data/esp32_partition_schemes.json",
        "https://raw.githubusercontent.com/hredan/esp-board-overview/refs/heads/main/web-app/data/esp32_mcu_bootloader_addr.json"
    ]
    
    for url in urls:
        filename = os.path.basename(url)
        save_path = os.path.join("esp_core_info", filename)
        if not os.path.exists(save_path):
            download_file(url, save_path)


def run_bash_command(command, cwd=None, timeout=120):
    """
    Runs a command in bash and returns a structured result.

    :param command: Command string to execute
    :param cwd: Optional working directory
    :param timeout: Timeout in seconds
    :return: dict with success, returncode, stdout, and stderr
    """
    try:
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
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "returncode": None,
            "stdout": e.stdout or "",
            "stderr": f"Command timed out after {timeout} seconds.",
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Unexpected error while running command: {e}",
        }