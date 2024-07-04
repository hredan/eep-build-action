#!/bin/bash

inputs=$@
param=""

# -s ${{ inputs.sketch-name }} -c ${{ inputs.core }} -b ${{ inputs.board }} -f ${{ inputs.cpu-frequency }} -v ${{ inputs.core-version }} -l ${{ inputs.libs }}

if [[ "$inputs" =~ ^-s (.*?) -c (.*?)]]; then
    name=${BASH_REMATCH[1]}
    echo "name: $name"
    core=${BASH_REMATCH[2]}
    echo "core: $core"
else
    echo "Invalid URL"
fi