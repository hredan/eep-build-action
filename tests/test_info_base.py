"""
Tests for the InfoBase module.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import json
from typing import Any

import pytest

from py_modules.info_base import InfoBase

partitions = {
    "eagle.flash.4m2m": [
        {
            "name": "sketch",
            "offset": "0x0",
            "size": "0xfeff0"
        },
        {
            "name": "empty",
            "offset": "0xfeff0",
            "size": "0x101010"
        },
        {
            "name": "spiffs",
            "offset": "0x200000",
            "size": "0x1fa000"
        },
        {
            "name": "eeprom",
            "offset": "0x3fb000",
            "size": "0x1000"
        },
        {
            "name": "rfcal",
            "offset": "0x3fc000",
            "size": "0x1000"
        },
        {
            "name": "wifi",
            "offset": "0x3fd000",
            "size": "0x3000"
        }
    ],
    "eagle.flash.4m": [
        {
            "name": "sketch",
            "offset": "0x0",
            "size": "0xfeff0"
        }
    ]
}


def test_info_base_get_partition_scheme() -> None:
    """Test that InfoBase can return the correct partition scheme."""
    info_base = InfoBase(partitions)
    # pylint: disable=protected-access
    scheme = info_base._get_partition_scheme("eagle.flash.4m2m")
    assert scheme == partitions["eagle.flash.4m2m"]


def test_info_base_get_partition_scheme_failed() -> None:
    """Test that InfoBase can return the correct partition scheme."""
    info_base = InfoBase(partitions)
    with pytest.raises(SystemExit):
        # pylint: disable=protected-access
        info_base._get_partition_scheme("eagle.flash.4m1m")


def test_info_base_get_spiffs_partition() -> None:
    """Test that InfoBase can return the correct SPIFFS partition."""
    info_base = InfoBase(partitions)
    # pylint: disable=protected-access
    scheme = info_base._get_partition_scheme("eagle.flash.4m2m")
    spiffs_partition = info_base._get_spiffs_partition(scheme)
    assert spiffs_partition == {
        "name": "spiffs",
        "offset": "0x200000",
        "size": "0x1fa000"
    }


def test_info_base_get_spiffs_partition_failed() -> None:
    """Test that InfoBase exits when the SPIFFS partition is missing."""
    info_base = InfoBase(partitions)
    # pylint: disable=protected-access
    scheme = info_base._get_partition_scheme("eagle.flash.4m")
    with pytest.raises(SystemExit):
        info_base._get_spiffs_partition(scheme)
