#!/bin/bash
set -e

COMPOSE="sudo COMPOSE_BAKE=true docker compose -f compose.test.yml"

# Run the test container and capture its exit code
$COMPOSE up --remove-orphans --abort-on-container-exit --exit-code-from test
EXIT_CODE=$?

# Cleanup
$COMPOSE down -v

# Exit with the captured code
exit $EXIT_CODE