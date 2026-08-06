"""
This script returns the mcu for a given board and core.

copyright (c) 2026 hredan
https://github.com/hredan/eep-build-action
"""
import sys
import argparse
from py_modules.esp32_info import Esp32Info

HELP_TEXT = (
    "Paramter:\n\n"
    "-c\tCORE\n\n"
    "-b\tBOARD\n\n"
    "get_mcu.py returns the mcu\n\n"
    "e.g. python3 ./get_mcu.py -b d1_mini -c esp8266\n"
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments compatible with the shell script."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-c", dest="core")
    parser.add_argument("-b", dest="board")
    parser.add_argument("-s", dest="sketch_name")
    parser.add_argument("-h", "--help", action="store_true", dest="show_help")
    return parser.parse_args()


def print_help() -> None:
    """Print the shell-compatible help text."""
    print(HELP_TEXT, end="")


def get_mcu(core: str, board: str) -> str:
    """Get the mcu for a given board and core."""
    if not core or not board:
        print("Error: core and board parameters are required.")
        raise SystemExit(1)

    if core == "esp32":

        esp32_info = Esp32Info()
        mcu = esp32_info.get_mcu_for_board(board)
        if not mcu:
            print(f"Error: Board '{board}' not found in ESP32 boards.")
            raise SystemExit(1)
        return mcu
    else:
        return "esp8266"


if __name__ == "__main__":
    args = parse_args()
    if args.show_help:
        print_help()
        sys.exit(0)
    print(get_mcu(args.core, args.board))
