#!/bin/bash

# Define the path to your Python script
C_script="/home/sulof/GPS/C/main.c"

#run gcc and make script ./output
gcc "$C_script" -o output

#run ./output
./output
