#!/bin/bash

# Navigate to the logs directory
cd logs/ || { echo "Failed to cd into logs/"; exit 1; }

# Clear the contents of each .log file
for file in *.log; do
    echo '' > "$file"
done