#!/bin/sh

export PYTHONPATH="$(cd "$(dirname "$0")" && pwd):$PYTHONPATH"

python -m dns-sync "$@"