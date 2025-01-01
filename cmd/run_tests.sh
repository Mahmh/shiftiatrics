#!/bin/bash
pytest tests -sv --cov=. --cov-report=html --cov-fail-under=80
cd tests/engine
sh run_engine_tests.sh