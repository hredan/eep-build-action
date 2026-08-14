"""
Module providing the base class for board information loading.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import sys

CORE_DATA_DIR = "esp_core_info"


class InfoBase:  # pylint: disable=too-few-public-methods
    """Base class providing JSON loading functionality for board information classes."""

    def __init__(self, partitions: dict[str, list[dict[str, str]]]):
        self.partitions = partitions

    def _get_spiffs_partition(self, scheme: list[dict[str, str]]) -> dict[str, str]:
        """Return the SPIFFS partition for the given partition scheme name, or None if not found."""
        for partition in scheme:
            if partition["name"] == "spiffs":
                return partition
        print(
            f"Error: SPIFFS partition not found in partition scheme '{scheme}'")
        sys.exit(1)

    def _get_partition_scheme(self, scheme_name: str) -> list[dict[str, str]]:
        """Return the partition scheme for the given scheme name, or an empty list if not found."""
        scheme = self.partitions.get(scheme_name)
        if scheme is None:
            print(
                f"Error: Partition scheme '{scheme_name}' not found in esp8266_partition_schemes.json")
            sys.exit(1)
        return scheme
