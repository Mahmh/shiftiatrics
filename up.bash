# #!/bin/bash
if [ "$1" == "--prod" ]; then
    echo 'Running production server'
    sudo docker compose -f compose.yml up --build
else
    echo 'Running dev server'
    sudo docker compose -f compose.yml -f compose.override.yml up --build
fi