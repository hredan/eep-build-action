#!/bin/bash
TOOL_DIR="./tools"
MKLITTLEFS_VERSION="3.0.0"
TOOL_URL="https://github.com/earlephilhower/mklittlefs/releases/download/$MKLITTLEFS_VERSION/x86_64-linux-gnu-mklittlefs-295fe9b.tar.gz"
TOOL=./tools/mklittlefs/mklittlefs
#check tool dir#
if [ ! -d "$TOOL_DIR" ]
	then
		echo "create $TOOL_DIR"
		mkdir $TOOL_DIR
fi

if [ ! -f "$TOOL" ]
	then
		echo "download and unpack mklittlefs"
		cd "$TOOL_DIR"
		wget "$TOOL_URL"
		tar -xf ./x86_64-linux-gnu-mklittlefs-295fe9b.tar.gz
		cd ..
fi
mkdir ./BIN_DATA
$TOOL -c ./data -p 256 -b 8192 -s 2072576 ./BIN_DATA/$1_littlefs.bin