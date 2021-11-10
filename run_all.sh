#!/bin/bash
# clean folder
git clean -xdf
# define sketch name
SKETCH_NAME=ESP_jQuery_Mobile_Interface
SCRIPT_DIR=./ESP_Action_Build_Scripts
#create data bin
sh $SCRIPT_DIR/build_data.sh $SKETCH_NAME
sh $SCRIPT_DIR/build_sketch.sh ESP8266
sh $SCRIPT_DIR/build_sketch.sh ESP32
sh $SCRIPT_DIR/save_raw_data.sh
sh $SCRIPT_DIR/create_eef_package.sh $SKETCH_NAME