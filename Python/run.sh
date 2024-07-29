#!/bin/bash

# Define the path to your Python script
PYTHON_SCRIPT="/home/sulof/GPS/Python/main.py"

# Define the interval in seconds between executions (e.g., 60 seconds)
INTERVAL=0

# Loop to continuously run the Python script
while true; do
    # Execute the Python script
    python3 "$PYTHON_SCRIPT"
    
    # Wait for the specified interval before running again
    sleep $INTERVAL
done

