#!/bin/bash
TOOL_DIR="./tools"
MKLITTLEFS_VERSION="3.0.0"
TOOL_URL="https://github.com/earlephilhower/mklittlefs/releases/download/$MKLITTLEFS_VERSION/x86_64-linux-gnu-mklittlefs-295fe9b.tar.gz"
TOOL=./tools/mklittlefs/mklittlefs
DATA_DIR=./data

HELP="Paramter:\n
-c\tCORE=esp8266/esp32 (mandatory)!\n
-s\tSketch name (mandatory)!\n
e.g. sh ./build_data.sh -s SKETCH_NAME -c esp32\n"

while getopts c:s:h: flag
do
    case "${flag}" in
        c) CORE=${OPTARG};;      
		s) SKETCH_NAME=${OPTARG};;		
		h) echo $HELP;;
    esac
done


if  [ -z ${SKETCH_NAME} &&  -z ${CORE}]
	then
		echo "ERROR: Sketch name or Core are not defined"
		echo $HELP
		exit 1
	else
		echo "### Build data starts with parameter: ###"
		echo "Sketch: $SKETCH_NAME"
		echo "Core:\t$CORE"		
fi

if [ -d "$DATA_DIR" ]; then
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

	if [ $CORE = "esp32" ]; then
		$TOOL -c ./data -p 256 -b 4096 -s 1507328 ./BIN_DATA/ESP32_${SKETCH_NAME}_littlefs.bin
	else
		$TOOL -c ./data -p 256 -b 8192 -s 2072576 ./BIN_DATA/ESP8266_${SKETCH_NAME}_littlefs.bin		
	fi
	
	if [ "$?" -ne "0" ]; then
		echo "Creation of littlefs failed"
		exit 1
	fi
else
	echo "No $DATA_DIR available, skip creation of littlefs binaries!"
fi