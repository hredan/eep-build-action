"""
Tests for the Helper module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import os
import subprocess
from typing import Any
from unittest.mock import MagicMock, patch, mock_open

import pytest
import requests.exceptions

from py_modules import helper


def test_run_bash_command_success() -> None:
    """Test that run_bash_command returns success for valid commands."""
    result = helper.run_bash_command("echo 'test'")

    assert result["success"] is True
    assert result["returncode"] == 0
    assert "test" in result["stdout"]


def test_run_bash_command_failure() -> None:
    """Test that run_bash_command returns failure for invalid commands."""
    result = helper.run_bash_command("exit 1")

    assert result["success"] is False
    assert result["returncode"] == 1


def test_run_bash_command_with_custom_cwd(tmp_path: Any) -> None:
    """Test that run_bash_command works with custom working directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    result = helper.run_bash_command("ls test.txt", cwd=str(tmp_path))

    assert result["success"] is True
    assert result["returncode"] == 0


def test_run_bash_command_timeout() -> None:
    """Test that run_bash_command handles timeout correctly."""
    result = helper.run_bash_command("sleep 5", timeout=1)

    # The command should either timeout or be treated as failure
    assert result["success"] is False


def test_run_bash_command_captures_stderr() -> None:
    """Test that run_bash_command captures stderr output."""
    result = helper.run_bash_command("echo 'error' >&2 && exit 1")

    assert result["success"] is False
    assert result["stderr"] != ""


def test_download_file_success() -> None:
    """Test that download_file successfully downloads a file."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content = MagicMock(return_value=[b"test data"])
        mock_get.return_value.__enter__.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.makedirs"):
                helper.download_file(
                    "http://example.com/file.txt", "/tmp/file.txt")
                mock_get.assert_called_once_with(
                    "http://example.com/file.txt", stream=True, timeout=15
                )


def test_download_file_invalid_url() -> None:
    """Test that download_file handles invalid URLs."""
    with patch("requests.get", side_effect=Exception("Invalid URL")):
        with patch("builtins.print") as mock_print:
            helper.download_file("invalid_url", "/tmp/file.txt")
            # Should print error message
            mock_print.assert_called()


def test_install_libs_with_valid_libs() -> None:
    """Test that install_libs runs install command for each library."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": True}

        helper.install_libs("library1,library2")

        # Should be called for each library
        assert mock_run.call_count >= 2


def test_install_libs_with_none() -> None:
    """Test that install_libs handles None input gracefully."""
    with patch.object(helper, "run_bash_command") as mock_run:
        helper.install_libs(None)

        # Should not call run_bash_command when libs is None
        mock_run.assert_not_called()


def test_install_libs_with_empty_string() -> None:
    """Test that install_libs handles empty string gracefully."""
    with patch.object(helper, "run_bash_command") as mock_run:
        helper.install_libs("")

        # Should not call run_bash_command when libs is empty
        mock_run.assert_not_called()


def test_install_libs_failure_exits() -> None:
    """Test that install_libs exits on installation failure."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": False, "stderr": "Error"}

        with pytest.raises(SystemExit):
            helper.install_libs("library1")


def test_compile_sketch_success() -> None:
    """Test that compile_sketch calls run_bash_command correctly."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": True}

        helper.compile_sketch("sketch", "./build", "esp32:esp32:esp32", "160")

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "compile" in call_args
        assert "--fqbn esp32:esp32:esp32" in call_args
        assert "sketch.ino" in call_args
        assert "./build" in call_args


def test_compile_sketch_without_cpu_freq() -> None:
    """Test that compile_sketch works without CPU frequency."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": True}

        helper.compile_sketch("sketch", "./build", "esp32:esp32:esp32")

        call_args = mock_run.call_args[0][0]
        assert "cpu_freq" not in call_args


def test_compile_sketch_failure_exits() -> None:
    """Test that compile_sketch exits on compilation failure."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": False, "stderr": "Compile error"}

        with pytest.raises(SystemExit):
            helper.compile_sketch("sketch", "./build", "esp32:esp32:esp32")


def test_download_arduino_cli() -> None:
    """Test that download_arduino_cli constructs correct URL."""
    with patch.object(helper, "download_file") as mock_download:
        with patch("os.path.exists", return_value=False):
            helper.download_arduino_cli("1.0.0")

            mock_download.assert_called_once()
            call_args = mock_download.call_args[0]
            assert "1.0.0" in call_args[0]
            assert "Linux_64bit.tar.gz" in call_args[0]


def test_download_arduino_cli_already_exists() -> None:
    """Test that download_arduino_cli skips if file already exists."""
    with patch.object(helper, "download_file") as mock_download:
        with patch("os.path.exists", return_value=True):
            helper.download_arduino_cli("1.0.0")

            mock_download.assert_not_called()


def test_install_core_with_version() -> None:
    """Test that install_core constructs correct commands with version."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": True}

        helper.install_core("esp32", "3.0.0")

        # Should be called at least twice (update-index and install)
        assert mock_run.call_count >= 2
        # Check that the core specification includes version
        install_call = [
            call for call in mock_run.call_args_list if "install" in str(call)][0]
        assert "@3.0.0" in str(install_call) or "3.0.0" in str(install_call)


def test_install_core_without_version() -> None:
    """Test that install_core works without version."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": True}

        helper.install_core("esp32")

        assert mock_run.call_count >= 2


def test_install_core_failure_exits() -> None:
    """Test that install_core exits on failure."""
    with patch.object(helper, "run_bash_command") as mock_run:
        mock_run.return_value = {"success": False,
                                 "stderr": "Installation failed"}

        with pytest.raises(SystemExit):
            helper.install_core("esp32", "3.0.0")


def test_install_core_update_index_failure_exits() -> None:
    """Test that install_core exits when updating index fails."""
    with patch.object(helper, "run_bash_command") as mock_run:
        # First call (update-index) fails
        mock_run.return_value = {"success": False, "stderr": "Update failed"}

        with pytest.raises(SystemExit):
            helper.install_core("esp32", "3.0.0")


def test_run_bash_command_with_stream_output() -> None:
    """Test that run_bash_command with stream_output=True handles output."""
    result = helper.run_bash_command("echo 'test'", stream_output=True)

    assert result["success"] is True
    assert result["returncode"] == 0
    assert "test" in result["stdout"]


def test_run_bash_command_stream_output_timeout() -> None:
    """Test that run_bash_command with stream_output handles timeout."""
    result = helper.run_bash_command("sleep 10", stream_output=True, timeout=1)

    assert result["success"] is False


def test_run_bash_command_stream_output_failure() -> None:
    """Test that run_bash_command with stream_output captures failure."""
    result = helper.run_bash_command("exit 1", stream_output=True)

    assert result["success"] is False
    assert result["returncode"] == 1


def test_run_bash_command_exception_handling() -> None:
    """Test that run_bash_command handles exceptions gracefully."""
    with patch("subprocess.run", side_effect=Exception("Test exception")):
        result = helper.run_bash_command("test_command")

        assert result["success"] is False
        assert result["returncode"] is None
        assert "Unexpected error" in result["stderr"]


def test_download_file_missing_schema_exception() -> None:
    """Test that download_file handles MissingSchema exception."""
    with patch("requests.get", side_effect=Exception("Invalid schema")):
        with patch("builtins.print") as mock_print:
            helper.download_file("invalid://url", "/tmp/file.txt")
            mock_print.assert_called()


def test_download_file_connection_error() -> None:
    """Test that download_file handles connection errors."""
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed")):
        with patch("builtins.print") as mock_print:
            helper.download_file(
                "http://invalid-host.example.com/file.txt", "/tmp/file.txt")
            # Verify error message was printed
            mock_print.assert_called()


def test_download_file_timeout() -> None:
    """Test that download_file handles timeout errors."""
    with patch("requests.get", side_effect=requests.exceptions.Timeout("Timeout")):
        with patch("builtins.print") as mock_print:
            helper.download_file(
                "http://example.com/slow-file.txt", "/tmp/file.txt")
            # Verify error message was printed
            mock_print.assert_called()


def test_download_file_http_error() -> None:
    """Test that download_file handles HTTP errors."""
    with patch("requests.get", side_effect=requests.exceptions.HTTPError("404 Not Found")):
        with patch("builtins.print") as mock_print:
            helper.download_file(
                "http://example.com/missing.txt", "/tmp/file.txt")
            mock_print.assert_called()


def test_download_json_files() -> None:
    """Test that download_json_files calls download_file for each required file."""
    with patch.object(helper, "download_file") as mock_download:
        with patch("os.path.exists", return_value=False):
            helper.download_json_files()

            # Should be called for each JSON file (5 files)
            assert mock_download.call_count == 5
            # Verify it's called with expected file patterns
            call_args_list = [call[0][0]
                              for call in mock_download.call_args_list]
            assert any("core_list.json" in arg for arg in call_args_list)
            assert any("esp8266.json" in arg for arg in call_args_list)
            assert any("esp32.json" in arg for arg in call_args_list)
            assert any(
                "esp32_partition_schemes.json" in arg for arg in call_args_list)
            assert any(
                "esp32_mcu_bootloader_addr.json" in arg for arg in call_args_list)


def test_download_json_files_skip_existing() -> None:
    """Test that download_json_files skips files that already exist."""
    with patch.object(helper, "download_file") as mock_download:
        with patch("os.path.exists", return_value=True):
            helper.download_json_files()

            # Should not download any files if they exist
            mock_download.assert_not_called()


def test_create_eep_esp8266(tmp_path: Any) -> None:
    """Test the _create_eep_esp8266 function creates correct EEF file."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    eep_dir = tmp_path / "eep"
    eep_dir.mkdir()

    config = MagicMock(spec=BuildConfig)
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "test_sketch"
    config.core = "esp8266"
    config.board = "esp8266_board"

    # Create necessary build files
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "test_sketch.ino.bin").write_bytes(b"app_data")

    with patch("shutil.copy2") as mock_copy:
        helper._create_eep_esp8266(config, str(
            eep_dir), "output", "littlefs.bin", False)

        mock_copy.assert_called()
        # Verify EEF file was created
        eef_files = list(eep_dir.glob("*.eef"))
        assert len(eef_files) > 0


def test_copy_esp32_binaries(tmp_path: Any) -> None:
    """Test the _copy_esp32_binaries function copies required binaries."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    eep_dir = tmp_path / "eep"
    eep_dir.mkdir()

    config = MagicMock(spec=BuildConfig)
    config.core = "esp32"
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "test_sketch"
    config.core_version = "3.0.0"

    # Create necessary build files
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "test_sketch.ino.bin").write_bytes(b"app")
    (build_dir / "test_sketch.ino.bootloader.bin").write_bytes(b"bootloader")
    (build_dir / "test_sketch.ino.partitions.bin").write_bytes(b"partitions")

    # Mock boot_app0.bin path
    boot_app_path = tmp_path / "boot_app0.bin"
    boot_app_path.write_bytes(b"boot_app0")

    with patch("os.path.expanduser", return_value=str(boot_app_path)):
        with patch("os.path.exists", return_value=True):
            app_name, boot_name, part_name = helper._copy_esp32_binaries(
                config, str(eep_dir), "output"
            )

            assert app_name == "esp32_output.ino.bin"
            assert boot_name == "esp32_output.ino.bootloader.bin"
            assert part_name == "esp32_output.ino.partitions.bin"


def test_copy_esp32_binaries_missing_boot_app0(tmp_path: Any) -> None:
    """Test that _copy_esp32_binaries raises error when boot_app0.bin is missing."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    eep_dir = tmp_path / "eep"
    eep_dir.mkdir()

    config = MagicMock(spec=BuildConfig)
    config.core = "esp32"
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "test_sketch"
    config.core_version = "3.0.0"

    # Create necessary build files
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "test_sketch.ino.bin").write_bytes(b"app")
    (build_dir / "test_sketch.ino.bootloader.bin").write_bytes(b"bootloader")
    (build_dir / "test_sketch.ino.partitions.bin").write_bytes(b"partitions")

    with patch("os.path.expanduser", return_value="/nonexistent/boot_app0.bin"):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Missing required file"):
                helper._copy_esp32_binaries(config, str(eep_dir), "output")


def test_create_eep_esp32(tmp_path: Any) -> None:
    """Test the _create_eep_esp32 function creates correct EEF file."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    eep_dir = tmp_path / "eep"
    eep_dir.mkdir()

    config = MagicMock(spec=BuildConfig)
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "test_sketch"
    config.core = "esp32"
    config.core_version = "3.0.0"
    config.get_mcu = MagicMock(return_value="esp32")
    config.get_bootloader_address = MagicMock(return_value="0x1000")

    # Create necessary build files
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "test_sketch.ino.bin").write_bytes(b"app")
    (build_dir / "test_sketch.ino.bootloader.bin").write_bytes(b"bootloader")
    (build_dir / "test_sketch.ino.partitions.bin").write_bytes(b"partitions")

    boot_app_path = tmp_path / "boot_app0.bin"
    boot_app_path.write_bytes(b"boot_app0")

    with patch("os.path.expanduser", return_value=str(boot_app_path)):
        with patch("os.path.exists", return_value=True):
            helper._create_eep_esp32(config, str(
                eep_dir), "output", "littlefs.bin", False)

            # Verify EEF file was created
            eef_files = list(eep_dir.glob("*.eef"))
            assert len(eef_files) > 0


def test_create_eep_dir_esp8266(tmp_path: Any, monkeypatch: Any) -> None:
    """Test create_eep_dir for ESP8266 core."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    monkeypatch.chdir(tmp_path)

    config = MagicMock(spec=BuildConfig)
    config.core = "esp8266"
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "blink"
    config.board = "nodemcu"

    # Create build directory
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "blink.ino.bin").write_bytes(b"app")

    bin_data_dir = tmp_path / "BIN_DATA"
    bin_data_dir.mkdir()

    with patch("shutil.copy2"):
        helper.create_eep_dir(config)

        # Verify EEP directory was created
        assert (tmp_path / "EEP").exists()
        # Verify readme.txt was created
        assert (tmp_path / "EEP" / "readme.txt").exists()


def test_create_eep_dir_esp32(tmp_path: Any, monkeypatch: Any) -> None:
    """Test create_eep_dir for ESP32 core."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    monkeypatch.chdir(tmp_path)

    config = MagicMock(spec=BuildConfig)
    config.core = "esp32"
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "blink"
    config.board = "esp32dev"
    config.core_version = "3.0.0"
    config.get_mcu = MagicMock(return_value="esp32")
    config.get_bootloader_address = MagicMock(return_value="0x1000")

    # Create build directory
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "blink.ino.bin").write_bytes(b"app")
    (build_dir / "blink.ino.bootloader.bin").write_bytes(b"bootloader")
    (build_dir / "blink.ino.partitions.bin").write_bytes(b"partitions")

    bin_data_dir = tmp_path / "BIN_DATA"
    bin_data_dir.mkdir()

    boot_app_path = tmp_path / "boot_app0.bin"
    boot_app_path.write_bytes(b"boot_app0")

    with patch("os.path.expanduser", return_value=str(boot_app_path)):
        with patch("shutil.copy2"):  # Mock file copying
            helper.create_eep_dir(config)

            # Verify EEP directory was created
            assert (tmp_path / "EEP").exists()
            # Verify readme.txt was created
            assert (tmp_path / "EEP" / "readme.txt").exists()


def test_create_eep_dir_unsupported_core(tmp_path: Any, monkeypatch: Any) -> None:
    """Test create_eep_dir raises error for unsupported core."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    monkeypatch.chdir(tmp_path)

    config = MagicMock(spec=BuildConfig)
    config.core = "unsupported_core"
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "blink"
    config.board = "test_board"

    # Create build directory
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    bin_data_dir = tmp_path / "BIN_DATA"
    bin_data_dir.mkdir()

    with pytest.raises(ValueError, match="Unsupported core"):
        helper.create_eep_dir(config)


def test_create_eep_dir_clears_existing(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that create_eep_dir clears existing EEP directory."""
    from unittest.mock import MagicMock
    from py_modules.build_config import BuildConfig

    monkeypatch.chdir(tmp_path)

    # Create existing EEP directory with files
    eep_dir = tmp_path / "EEP"
    eep_dir.mkdir()
    (eep_dir / "old_file.bin").write_bytes(b"old")

    config = MagicMock(spec=BuildConfig)
    config.core = "esp8266"
    config.build_path = str(tmp_path / "build")
    config.sketch_name = "blink"
    config.board = "nodemcu"

    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "blink.ino.bin").write_bytes(b"app")

    bin_data_dir = tmp_path / "BIN_DATA"
    bin_data_dir.mkdir()

    with patch("shutil.copy2"):
        helper.create_eep_dir(config)

        # Verify old file was removed
        assert not (eep_dir / "old_file.bin").exists()
