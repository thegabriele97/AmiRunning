#!/bin/sh

# vars
ROOT_PROJECT="/home/gabri97/AmIRunning-code/"
PATH_RASPBERRY="$ROOT_PROJECT/src/RaspberryPi/"
START_SCRIPT="main.py"
PY_INTERPRETER="/usr/local/bin/python3"
LOG_DIR="/home/gabri97/"
DEFAULT_CONFIG_FILE="$ROOT_PROJECT/configs_polito.json"

if [ $# -eq 1 ]; then
    DEFAULT_CONFIG_FILE=$1
fi

# starting server
$PY_INTERPRETER $(realpath "$PATH_RASPBERRY/$START_SCRIPT") $(realpath $DEFAULT_CONFIG_FILE) > $LOG_DIR/log.txt 2>&1 &

exit 0
