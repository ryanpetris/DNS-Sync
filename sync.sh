#!/bin/sh

export PYTHONPATH="$(cd "$(dirname "$0")" && pwd):$PYTHONPATH"

python -u -m dns-sync "$@"
