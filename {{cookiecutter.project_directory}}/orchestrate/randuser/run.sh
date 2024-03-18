#!/bin/bash

set -eu

################################################################
## SET CONSTANTS

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

RANDUSER_EXTRACT_PATH="../../extract/randuser/extract/"
RANDUSER_LOAD_PATH="../../extract/randuser/load/"


################################################################
## EXECUTE EXTRACT TASKS

# randuser-extract

cd $RANDUSER_EXTRACT_PATH
python -m venv .venv
.venv/bin/pip install -r requirements.txt
export APP_OBJ_URI=$(.venv/bin/python -m main)
cd $SCRIPT_DIR


# randuser-load

cd $RANDUSER_LOAD_PATH
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m main
cd $SCRIPT_DIR
