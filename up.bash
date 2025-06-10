#!/bin/bash
if [ "$1" == "--prod" ]; then
    echo 'Running production server'
    sudo COMPOSE_BAKE=true docker compose -f compose.yml up --build -d
else
    echo 'Running dev server'
    sudo COMPOSE_BAKE=true docker compose -f compose.yml -f compose.override.yml up --build
fi