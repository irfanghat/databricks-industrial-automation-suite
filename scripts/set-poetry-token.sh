#!/bin/bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <PYPI_TOKEN>"
  exit 1
fi

TOKEN="$1"

CURRENT_DIR="$(pwd)"

echo "Setting Poetry PyPI token..."
poetry config pypi-token.pypi "$TOKEN"

echo "PyPI token configured successfully in Poetry."