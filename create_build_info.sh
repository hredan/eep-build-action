#!/bin/bash
TOOL_DIR="./tools"
HELP="Paramter:\n
-s\tGITHUB_SHA\n
-r\tGITHUB_REPOSITORY\n
e.g. sh ./create_build_info.sh -s \$GITHUB_SHA -r \$GITHUB_REPOSITORY\n"

while getopts s:r:h flag
do
    case "${flag}" in
        s) SHA=${OPTARG};;
        r) REPO_NAME=${OPTARG};;		
        h) echo -e $HELP; exit 0;
    esac
done

case $OSTYPE in
    linux-gnu)
        TOOL=./tools/arduino-cli
        ;;
    msys)
        TOOL=./tools/arduino-cli.exe
        ;;
    *)
        echo "OS: $OSTYPE currently not supported!"
        exit 1
        ;;
esac

# store data in EEP
EEP_DIR=./EEP
INFO_FILE_PATH=$EEP_DIR/build_info.txt
if [ -d $EEP_DIR ]; then
    echo -e "Repository URL: www.github.com/$REPO_NAME" > $INFO_FILE_PATH
    echo -e "GITHUB_SHA:     $SHA" >> $INFO_FILE_PATH
    
    if [ -f $TOOL ]; then
        CORE_TEXT=$($TOOL core list)
        echo -e "\n### Core Versions ###\n$CORE_TEXT" >> $INFO_FILE_PATH

        LIBS_TEXT=$($TOOL lib list)
        echo -e "\n### LIB Versions ###\n$LIBS_TEXT" >> $INFO_FILE_PATH
    fi
else
    echo "Error: could not create build_info.txt"
    echo "Error: $EEP_DIR does not exsist!"
fi
