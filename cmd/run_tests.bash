#!/bin/bash
set -e

COMPOSE="sudo docker compose -f compose.test.yml"

# Run the test container and capture its exit code
$COMPOSE up --build --abort-on-container-exit --exit-code-from test
EXIT_CODE=$?

# Cleanup
$COMPOSE down -v

# Exit with the captured code
exit $EXIT_CODE