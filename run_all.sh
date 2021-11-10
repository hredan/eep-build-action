#!/bin/bash
# clean folder
git clean -xdf
# define sketch name
SKETCH_NAME=ESP_jQuery_Mobile_Interface
SCRIPT_DIR=./ESP_Action_Build_Scripts

ESP8266_VERSION=3.0.2
ESP32_VERSION=2.0.1

#create data bin
sh $SCRIPT_DIR/build_data.sh $SKETCH_NAME
sh $SCRIPT_DIR/build_sketch.sh ESP8266 $ESP8266_VERSION
sh $SCRIPT_DIR/build_sketch.sh ESP32 $ESP32_VERSION
sh $SCRIPT_DIR/save_raw_data.sh
sh $SCRIPT_DIR/create_eef_package.sh $SKETCH_NAME $ESP32_VERSION