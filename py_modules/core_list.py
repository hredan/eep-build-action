"""
Module for loading and providing the list of supported Arduino cores.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import sys

from py_modules.info_base import InfoBase, CORE_DATA_DIR


class CoreList(InfoBase):
    """Provides the list of supported Arduino cores and their versions."""

    def __init__(self):
        try:
            self.cores = self.load_json(f"{CORE_DATA_DIR}/core_list.json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error initializing CoreList: {e}")
            sys.exit(1)

    def get_core_version(self, core_name):
        """Return the latest version string for the given core name, or None if not found."""
        for core in self.cores:
            if core["core_name"] == core_name:
                return core["latest_version"]
        return None
