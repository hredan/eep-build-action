#!/bin/bash
SCRIPT_DIR=${0%/*}
TOOL_DIR="./tools"
ARDUINO_CLI_VERSION="0.26.0"

BIN_DATA_DIR=./BIN_DATA

#default settings
CORE=esp8266
BOARD=d1_mini
CPUF=160
LIBS=""

HELP="Paramter:\n
-c\tCORE esp8266/esp32\n
-b\tBOARD e.g. d1_mini or d1_mini32\n
-l\tLIBS comma seperated Lib names e.g. U8g2,RTClib\n
-f\tCPU Frequence e.g. 80, 160 or 240\n
-s\tSketch name (mandatory)!\n
-v\tcore version\n
e.g. sh ./build_sketch.sh -s SKETCH_NAME\n"

while getopts c:b:f:l:s:v:h flag
do
    case "${flag}" in
        c) CORE=${OPTARG};;
        b) BOARD=${OPTARG};;
		l) LIBS=${OPTARG};;
        f) CPUF=${OPTARG};;
		s) SKETCH_NAME=${OPTARG};;
		v) CORE_VERSION=${OPTARG};;
		h) echo -e $HELP; exit 0;
    esac
done

# set TOOL_URL and TOOL PATH (depends on OS)
#check tool dir#
if [ ! -d "$TOOL_DIR" ]
	then
		echo "## create $TOOL_DIR ##"
		mkdir $TOOL_DIR
fi

if [ ! -f "$TOOL" ]; then
	echo "## download and unpack ARDUINO_CLI ##"
	cd "$TOOL_DIR"

	case $OSTYPE in
		linux-gnu)
			TOOL_ACHIVE_NAME="arduino-cli_${ARDUINO_CLI_VERSION}_Linux_64bit.tar.gz"
			TOOL_URL="https://github.com/arduino/arduino-cli/releases/download/${ARDUINO_CLI_VERSION}/$TOOL_ACHIVE_NAME"
			TOOL=./tools/arduino-cli
			curl -kLSs $TOOL_URL -o $TOOL_ACHIVE_NAME
			tar -xf ./$TOOL_ACHIVE_NAME
			;;
		msys)
			TOOL_ACHIVE_NAME="arduino-cli_${ARDUINO_CLI_VERSION}_Windows_64bit.zip"
			TOOL_URL="https://github.com/arduino/arduino-cli/releases/download/${ARDUINO_CLI_VERSION}/$TOOL_ACHIVE_NAME"
			TOOL=./tools/arduino-cli.exe
			curl -kLSs $TOOL_URL -o $TOOL_ACHIVE_NAME
			unzip -o $TOOL_ACHIVE_NAME
			;;
		*)
			echo "OS: $OSTYPE currently not supported!"
			exit 1
			;;
	esac
	cd ..
fi
# get summary
if [ -z ${SKETCH_NAME} ]
	then
		echo "ERROR: Sketch name not defined"
		echo -e $HELP
		exit 1
	else
		echo "### Build starts with parameter: ###"
		echo "Sketch: $SKETCH_NAME"
		echo -e "Core:\t$CORE"
		echo -e "Board:\t$BOARD"
		echo -e "LIBS:\t$LIBS"
		echo -e "CPU F:\t$CPUF"
		echo -e "Version:\t$CORE_VERSION"
fi

# create littlefs binaries if data is available
bash $SCRIPT_DIR/build_data.sh -c $CORE -s $SKETCH_NAME
if [ "$?" -ne "0" ]; then
	echo "Creation of littlefs failed"
	exit 1
fi

if [ $CORE = "esp32" ]
	then
		BUILD_DIR=./BIN_${CORE}_${BOARD}
		CACHE_DIR=./CACHE_${CORE}
		CORE_URL="https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_dev_index.json"
		FQBN_PARA="esp32:esp32:$BOARD:FlashFreq=80,PartitionScheme=default,CPUFreq=$CPUF,UploadSpeed=921600"
		if [ -z $CORE_VERSION ]; then CORE_NAME=esp32:esp32; else CORE_NAME=esp32:esp32@$CORE_VERSION; fi		
	else	
		BUILD_DIR=./BIN_ESP8266_$BOARD
		CACHE_DIR=./CACHE_ESP8266
		CORE_URL="https://arduino.esp8266.com/stable/package_esp8266com_index.json"
		FQBN_PARA="esp8266:esp8266:$BOARD:xtal=$CPUF,vt=flash,exception=disabled,stacksmash=disabled,ssl=all,mmu=3232,non32xfer=fast,eesz=4M2M,ip=hb2f,dbg=Disabled,lvl=None____,wipe=none,baud=921600"
		if [ -z $CORE_VERSION ]; then CORE_NAME=esp8266:esp8266; else CORE_NAME=esp8266:esp8266@$CORE_VERSION; fi
fi

if [ -d $BUILD_DIR ]; then
	rm rm -r -f $BUILD_DIR
fi	

echo "## Create output directories ##"
mkdir $BUILD_DIR
mkdir $CACHE_DIR

echo "## install core ##"
$TOOL core update-index --additional-urls $CORE_URL
$TOOL core install $CORE_NAME --additional-urls $CORE_URL
if [ "$?" -ne "0" ]; then
	echo "Core installation failed with errorcode $?"
	exit 1
fi

echo "## install needed libs ##"
IFS="," read -a lib_arr <<< $LIBS
for lib in ${lib_arr[@]}
do
	echo "Install Lib: $lib"
	$TOOL lib install $lib
done

echo "## Start compiling ##"
$TOOL compile --fqbn $FQBN_PARA --build-path $BUILD_DIR --build-cache-path $CACHE_DIR $SKETCH_NAME.ino
if [ "$?" -ne "0" ]; then
	echo "Compilation failed with errorcode $?"
	exit 1
fi

# store data in EEP
EEP_DIR=./EEP
if [ ! -d $EEP_DIR ]; then
	mkdir $EEP_DIR
else
	# cleanup EEP directory before copy files to creating eef package (eep)
	rm -r ${EEP_DIR}/*
fi

# check are data available
if [ -d $BIN_DATA_DIR ]
	then
		CHECK_DATA=1
	else
		CHECK_DATA=0
fi

CORE_TEXT=$($TOOL core search $CORE:$CORE)
echo -e "### Core Version ###\n$CORE_TEXT"

LIBS_TEXT=$($TOOL lib list)
echo -e "### LIB Versions ###\n$LIBS_TEXT"

OUPUT_NAME=${BOARD}_${SKETCH_NAME}
if [ $CORE = "esp8266" ]; then
	echo "Save $CORE data for eef package"
	ESPTOOL_PARA_ESP8266="\"--baud\", \"460800\", \"write_flash\", \"0x0\", \"${CORE}_${OUPUT_NAME}.ino.bin\""
	ESPTOOL_PARA_FS=", \"0x200000\", \"${CORE}_${SKETCH_NAME}_littlefs.bin\""

	ESP8266_EEF_PATH=$EEP_DIR/${CORE}_${BOARD}_${SKETCH_NAME}.eef
	cp ${BUILD_DIR}/${SKETCH_NAME}.ino.bin ${EEP_DIR}/${CORE}_${OUPUT_NAME}.ino.bin
	if [ $CHECK_DATA -eq 0 ]; then
		echo -e "{\n\t\"command\": [${ESPTOOL_PARA_ESP8266}]\n}" > $ESP8266_EEF_PATH
	else
		cp ${BIN_DATA_DIR}/${CORE}_${SKETCH_NAME}_littlefs.bin ${EEP_DIR}
		echo -e "{\n\t\"command\": [${ESPTOOL_PARA_ESP8266}${ESPTOOL_PARA_FS}]\n}" > $ESP8266_EEF_PATH
	fi
fi

if [ $CORE = "esp32" ]; then
	echo "Save $CORE data for eef package"	
	ESPTOOL_PARA_ESP32="\"command\": [\"--chip\", \"esp32\", \"--baud\", \"921600\", \"--before\", \"default_reset\", \"--after\", \"hard_reset\", \"write_flash\", \"-z\", \"--flash_mode\", \"dio\", \"--flash_freq\", \"80m\", \"--flash_size\", \"detect\""
	ESPTOOL_PARA_ESP32_FILES=", \"0xe000\", \"boot_app0.bin\", \"0x1000\", \"${CORE}_${OUPUT_NAME}.ino.bootloader.bin\", \"0x10000\", \"${CORE}_${OUPUT_NAME}.ino.bin\", \"0x8000\", \"${CORE}_${OUPUT_NAME}.ino.partitions.bin\""
	ESPTOOL_PARA_ESP32_FS=", \"0x290000\", \"${CORE}_${SKETCH_NAME}_littlefs.bin\""
	ESP32_EEF_PATH=$EEP_DIR/${CORE}_${OUPUT_NAME}.eef
	
	
	if [ -z $CORE_VERSION ]; then
		# get core version
		CORE_VERSION=$(echo $CORE_TEXT | gawk '{ match($0, /([0-9]+\.[0-9]+\.[0-9]+)/, arr); if(arr[1] != "") print arr[1] }')
	fi
	
	BOOT_APP_PATH=~/.arduino15/packages/esp32/hardware/esp32/${CORE_VERSION}/tools/partitions/boot_app0.bin
	
	if [ ! -f $BOOT_APP_PATH ]; then
		echo "ERROR: could not find $BOOT_APP_PATH"
		exit 1
	else
		cp $BOOT_APP_PATH ${EEP_DIR}
	fi 
	
	cp ${BUILD_DIR}/${SKETCH_NAME}.ino.bin ${EEP_DIR}/${CORE}_${OUPUT_NAME}.ino.bin
	cp ${BUILD_DIR}/${SKETCH_NAME}.ino.bootloader.bin ${EEP_DIR}/${CORE}_${OUPUT_NAME}.ino.bootloader.bin
	cp ${BUILD_DIR}/${SKETCH_NAME}.ino.partitions.bin ${EEP_DIR}/${CORE}_${OUPUT_NAME}.ino.partitions.bin
	if [ $CHECK_DATA -eq 0 ]; then
		echo -e "{\n\t${ESPTOOL_PARA_ESP32}${ESPTOOL_PARA_ESP32_FILES}]\n}" > $ESP32_EEF_PATH
	else
		echo -e "{\n\t${ESPTOOL_PARA_ESP32}${ESPTOOL_PARA_ESP32_FILES}${ESPTOOL_PARA_ESP32_FS}]\n}" > $ESP32_EEF_PATH
		cp ${BIN_DATA_DIR}/${CORE}_${SKETCH_NAME}_littlefs.bin ${EEP_DIR}
	fi
fi

# write readme.txt
README_PATH="$EEP_DIR/readme.txt"
if [ ! -f $README_PATH ]; then
	echo "This package can be used with ESPEasyFlasher2.0 (https://github.com/hredan/ESPEASYFLASHER_2.0)" > $README_PATH
fi
