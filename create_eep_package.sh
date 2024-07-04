#!/bin/bash
SCRIPT_DIR=${0%/*}

HELP="Paramter:\n
-c\tCORE\n
-b\tBOARD\n
-s\tSketch\n
use the same parameter which are used for the build script\n
e.g. bash ./create_eef_package.sh -s MySketchName -b d1_mini -c esp8266\n"

while getopts c:b:s:h flag
do
    case "${flag}" in
        c) CORE=${OPTARG};;
        b) BOARD=${OPTARG};;
		s) SKETCH_NAME=${OPTARG};;
		h) echo -e $HELP; exit 0;
    esac
done

if [ -z ${SKETCH_NAME} ] || [ -z ${CORE} ] || [ -z ${BOARD} ]
	then
		echo "ERROR: Sketch name ,Core or Board not defined"
		echo -e $HELP
		exit 1
	else
		echo "### create eef package (eep): ###"
fi
EEP_DIR=./EEP
# create zip file (eef package)
if [ -d ${EEP_DIR} ]; then
     zip -j ${CORE}_${BOARD}_${SKETCH_NAME}.eep ${EEP_DIR}/*
else
    echo "Error could not find directory "
	exit 1
fi