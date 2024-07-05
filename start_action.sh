#!/bin/bash
SCRIPT_DIR=${0%/*}
PARAMS=""

echo Name: $INPUT_SKETCH_NAME
echo Core: $INPUT_CORE
echo Board: $INPUT_BOARD
echo CPU_f:$INPUT_CPU_F
echo CORE Version: $INPUT_CORE_VERSION
echo LIBS: $INPUT_LIBS

# create parameter string
if [ -n "$INPUT_SKETCH_NAME" ]; then
  PARAMS="$PARAMS -s $INPUT_SKETCH_NAME"
fi

if [ -n "$INPUT_CORE" ]; then
  PARAMS="$PARAMS -c $INPUT_CORE"
fi

if [ -n "$INPUT_BOARD" ]; then
  PARAMS="$PARAMS -b $INPUT_BOARD"
fi

if [ -n "$INPUT_CPU_F" ]; then
  PARAMS="$PARAMS -f $INPUT_CPU_F"
fi

if [ -n "$INPUT_CORE_VERSION" ]; then
  PARAMS="$PARAMS -v $INPUT_CORE_VERSION"
fi

if [ -n "$INPUT_LIBS" ]; then
  PARAMS="$PARAMS -l $INPUT_LIBS"
fi
echo PARAMS: $PARAMS

# run build_sketch.sh with parameters
$SCRIPT_DIR/build_sketch.sh $PARAMS