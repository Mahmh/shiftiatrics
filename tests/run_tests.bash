#!/bin/bash
if ! pytest tests -sv --cov=. --cov-report=html --cov-fail-under=85; then
    exit 1
fi

cd tests/engine
if ! sh run_engine_tests.sh; then
    exit 1
fi