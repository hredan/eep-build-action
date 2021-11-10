#!/bin/bash
#$1 defines the name of the sketch
#$2 defines the ESP32 core version, e.g. 2.0.1
#
#example call: sh .ESP_Action_Build_Scripts/create_eef_package.sh ESP_jQuery_Mobile_Interface 2.0.1
ARTIFACT_DIR="./Artifacts"
ESP8266_BUILD_DIR=./BIN_ESP8266
ESP32_BUILD_DIR=./BIN_ESP32
BIN_DATA_DIR=./BIN_DATA

EEP_DIR=./EEP

CHECK_ESP8266=0
CHECK_ESP32=0
CHECK_DATA=0

if [ ! -d $ARTIFACT_DIR ]
	then
		mkdir $ARTIFACT_DIR
fi

if [ -d $ESP8266_BUILD_DIR ]
	then
		CHECK_ESP8266=1
fi

if [ -d $ESP32_BUILD_DIR ]
	then
		CHECK_ESP32=1
fi

if [ -d $BIN_DATA_DIR ]
	then
		CHECK_DATA=1
fi

if [ -f $1.eep ]
	then
		rm $1.eep
fi

if [ $CHECK_ESP8266 -eq 0 ] && [ $CHECK_ESP32 -eq 0 ]; then
	echo "ERROR: can not create eep without data"
	exit 1
else
	echo "start creation of eep CHECK_ESP8266=$CHECK_ESP8266 CHECK_ESP32=$CHECK_ESP32 CHECK_DATA=$CHECK_DATA"
fi

# delete target dir and create an empty new target
if [ -d $EEP_DIR ]
	then
		rm rm -r -f $EEP_DIR
fi
mkdir $EEP_DIR

if [ $CHECK_DATA -eq 1 ]; then
	cp ${BIN_DATA_DIR}/${1}_littlefs.bin ${EEP_DIR}
fi

if [ $CHECK_ESP8266 -eq 1 ]; then
	ESPTOOL_PARA_ESP8266="\"--baud\", \"460800\", \"write_flash\", \"0x0\", \"ESP8266_${1}.ino.bin\""
	ESPTOOL_PARA_FS=", \"0x200000\" \"${1}_littlefs.bin\""

	ESP8266_EEF_PATH=$EEP_DIR/ESP8266_$1.eef
	cp ${ESP8266_BUILD_DIR}/${1}.ino.bin ${EEP_DIR}/ESP8266_${1}.ino.bin
	if [ $CHECK_DATA -eq 0 ]; then
		echo "{\n\t\"command\": [${ESPTOOL_PARA_ESP8266}]\n}" > $ESP8266_EEF_PATH
	else
		echo "{\n\t\"command\": [${ESPTOOL_PARA_ESP8266}${ESPTOOL_PARA_FS}]\n}" > $ESP8266_EEF_PATH
	fi
fi

if [ $CHECK_ESP32 -eq 1 ]; then
	ESPTOOL_PARA_ESP32="\"command\": [\"--chip\", \"esp32\", \"--baud\", \"921600\", \"--before\", \"default_reset\", \"--after\", \"hard_reset\", \"write_flash\", \"-z\", \"--flash_mode\", \"dio\", \"--flash_freq\", \"80m\", \"--flash_size\", \"detect\""
	ESPTOOL_PARA_ESP32_FILES=", \"0xe000\", \"boot_app0.bin\", \"0x1000\", \"ESP32_${1}.ino.bootloader.bin\", \"0x10000\", \"ESP32_${1}.ino.bin\", \"0x8000\", \"ESP32_${1}.ino.partitions.bin\""
	ESPTOOL_PARA_ESP32_FS=", \"0x210000\", \"${1}_littlefs.bin\""
	ESP32_EEF_PATH=$EEP_DIR/ESP32_$1.eef
	
	cp ~/.arduino15/packages/esp32/hardware/esp32/${2}/tools/partitions/boot_app0.bin ${EEP_DIR}
	cp ${ESP32_BUILD_DIR}/${1}.ino.bin ${EEP_DIR}/ESP32_${1}.ino.bin
	cp ${ESP32_BUILD_DIR}/${1}.bootloader.ino.bin ${EEP_DIR}/ESP32_${1}.ino.bootloader.bin
	cp ${ESP32_BUILD_DIR}/${1}.ino.partitions.bin ${EEP_DIR}/ESP32_${1}.ino.partitions.bin
	if [ $CHECK_DATA -eq 0 ]; then
		echo "{\n\t${ESPTOOL_PARA_ESP32}${ESPTOOL_PARA_ESP32_FILES}]\n}" > $ESP32_EEF_PATH
	else
		echo "{\n\t${ESPTOOL_PARA_ESP32}${ESPTOOL_PARA_ESP32_FILES}${ESPTOOL_PARA_ESP32_FS}]\n}" > $ESP32_EEF_PATH
	fi
fi

if [ -d $EEP_DIR ]
	then
		echo "create eef package"
		cd $EEP_DIR
		zip -r .$ARTIFACT_DIR/$1.eep .
		cd ..
fi



