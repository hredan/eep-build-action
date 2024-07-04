#!/bin/bash
TOOL_DIR="./tools"
HELP="Paramter:\n
-s\tGITHUB_SHA\n
-r\tGITHUB_REPOSITORY\n
-t\tTAG_NAME\n
e.g. sh ./create_build_info.sh -s \$GITHUB_SHA -r \$GITHUB_REPOSITORY\n"

while getopts s:r:t:h flag
do
    case "${flag}" in
        s) SHA=${OPTARG};;
        r) REPO_NAME=${OPTARG};;
        t) TAG_NAME=${OPTARG};;
        h) echo -e $HELP; exit 0;
    esac
done

case $OSTYPE in
    linux-gnu)
        CLI=./tools/arduino-cli
        MKL=./tools/mklittlefs/mklittlefs
        ;;
    msys)
        CLI=./tools/arduino-cli.exe
        MKL=./tools/mklittlefs/mklittlefs.exe 
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
    echo -e "Repository URL:  www.github.com/$REPO_NAME" > $INFO_FILE_PATH
    echo -e "GITHUB_SHA:      $SHA" >> $INFO_FILE_PATH
    if [ ! -z ${TAG_NAME} ]; then
        echo -e "Release version: ${TAG_NAME}" >> $INFO_FILE_PATH
    fi


    if [ -f $MKL ]; then
        MKL_VERSION=$($MKL --version)
    fi

    if [ -f $CLI ]; then
        echo -e "\n### Tools ###" >> $INFO_FILE_PATH
        echo $($CLI version) >> $INFO_FILE_PATH
        if [ ! -z ${MKL_VERSION+x} ]; then
            echo "$MKL_VERSION" >> $INFO_FILE_PATH
        fi

        CORE_TEXT=$($CLI core list)
        echo -e "\n### Core Versions ###\n$CORE_TEXT" >> $INFO_FILE_PATH

        LIBS_TEXT=$($CLI lib list)
        echo -e "\n### LIB Versions ###\n$LIBS_TEXT" >> $INFO_FILE_PATH
    fi
else
    echo "Error: could not create build_info.txt"
    echo "Error: $EEP_DIR does not exsist!"
    exit 1
fi
