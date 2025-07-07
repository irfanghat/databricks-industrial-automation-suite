#!/bin/bash

set -e

CURRENT_DIR=$(pwd)

rm -rf "$CURRENT_DIR/dist/"

poetry build

WHEEL_PATH=$(find "$CURRENT_DIR/dist/" -name "*.whl" | head -n 1)

poetry run pip install "$WHEEL_PATH" --force-reinstall
