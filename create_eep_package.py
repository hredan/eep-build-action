"""
Create an EEP package ZIP archive from the EEP directory contents.

Copyright (C) 2026 hredan
https://github.com/hredan/eep-build-action
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from py_modules.esp32_info import Esp32Info


HELP_TEXT = (
	"Paramter:\n\n"
	"-c\tCORE\n\n"
	"-b\tBOARD\n\n"
	"-s\tSketch\n\n"
	"use the same parameter which are used for the build script\n\n"
	"e.g. python3 ./create_eep_package.py -s MySketchName -b d1_mini -c esp8266\n"
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


def create_eep_package(core: str, board: str, sketch_name: str) -> Path:
	"""Create the .eep archive from files stored in ./EEP."""
	eep_dir = Path("./EEP")
	if not eep_dir.is_dir():
		print("Error could not find directory ")
		raise SystemExit(1)

	output_path = Path(f"{core}_{board}_{sketch_name}.eep")
	source_files = sorted(path for path in eep_dir.iterdir() if path.is_file())
	if not source_files:
		print("Error could not find files in directory ./EEP")
		raise SystemExit(1)

	with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
		for source_file in source_files:
			archive.write(source_file, arcname=source_file.name)

	return output_path


def main() -> int:
	"""Run the EEP package creation workflow."""
	args = parse_args()
	if args.show_help:
		print_help()
		return 0

	if not args.sketch_name or not args.core or not args.board:
		print("ERROR: Sketch name ,Core or Board not defined")
		print_help()
		return 1

	print("### create eep package (eep): ###")
	if args.core == "esp32":
		esp32_info = Esp32Info()
		mcu = esp32_info.get_mcu_for_board(args.board)
		if mcu:
			create_eep_package(mcu, args.board, args.sketch_name)
			return 0

	create_eep_package(args.core, args.board, args.sketch_name)
	return 0


if __name__ == "__main__":
	sys.exit(main())
