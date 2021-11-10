#!/bin/bash
TOOL_DIR="./tools"
ARDUINO_CLI_VERSION="0.19.3"
TOOL_URL="https://github.com/arduino/arduino-cli/releases/download/${ARDUINO_CLI_VERSION}/arduino-cli_${ARDUINO_CLI_VERSION}_Linux_64bit.tar.gz"
TOOL=./tools/arduino-cli

if [ $1 = "ESP32" ]
	then
		BUILD_DIR=./BIN_ESP32
		CACHE_DIR=./CACHE_ESP32
		CORE_URL="https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_dev_index.json"
		FQBN_PARA="esp32:esp32:lolin32:FlashFreq=80,PartitionScheme=default,CPUFreq=160,UploadSpeed=921600"
		CORE_NAME=esp32:esp32@${2}
	else	
		BUILD_DIR=./BIN_ESP8266
		CACHE_DIR=./CACHE_ESP8266
		CORE_URL="https://arduino.esp8266.com/stable/package_esp8266com_index.json"
		FQBN_PARA="esp8266:esp8266:d1_mini:xtal=160,vt=flash,exception=disabled,stacksmash=disabled,ssl=all,mmu=3232,non32xfer=fast,eesz=4M2M,ip=hb2f,dbg=Disabled,lvl=None____,wipe=none,baud=921600"
		CORE_NAME=esp8266:esp8266@${2}
fi
#check tool dir#
if [ ! -d "$TOOL_DIR" ]
	then
		echo "## create $TOOL_DIR ##"
		mkdir $TOOL_DIR
fi

if [ ! -f "$TOOL" ]
	then
		echo "## download and unpack mklittlefs ##"
		cd "$TOOL_DIR"
		wget "$TOOL_URL"
		tar -xf ./arduino-cli_${ARDUINO_CLI_VERSION}_Linux_64bit.tar.gz
		cd ..
fi

echo "## Create output directories ##"
mkdir $BUILD_DIR
mkdir $CACHE_DIR

echo "## install core ##"
$TOOL core update-index --additional-urls $CORE_URL
$TOOL core install $CORE_NAME --additional-urls $CORE_URL

echo "## Start compiling ##"
$TOOL compile --fqbn $FQBN_PARA --build-path $BUILD_DIR --build-cache-path $CACHE_DIR ESP_jQuery_Mobile_Interface.ino