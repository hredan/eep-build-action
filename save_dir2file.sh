#!/bin/bash

if [ -d $1 ]
	then
		echo "store all data of $1"
		zip -r $2 $1
	else
		echo "ERROR: could not find $1"
fi
