#!/bin/bash
# Quick RC Car Control Script
# Usage: ./quick_control.sh [command]
# Commands: w, s, a, d, space, c, x

PI_HOST="${PI_HOST:-raspberrypi.local}"
PI_USER="${PI_USER:-pi}"
SCRIPT_PATH="${SCRIPT_PATH:-~/rc_car_control/arduino_wasd_controller.py}"

if [ $# -eq 0 ]; then
    echo "RC Car Quick Control"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  w      - Forward"
    echo "  s      - Backward"
    echo "  a      - Steer left"
    echo "  d      - Steer right"
    echo "  space  - Stop drive"
    echo "  c      - Center steering"
    echo "  x      - All off"
    echo ""
    echo "Environment variables:"
    echo "  PI_HOST     - Raspberry Pi hostname (default: raspberrypi.local)"
    echo "  PI_USER     - SSH username (default: pi)"
    echo "  SCRIPT_PATH - Path to controller script on Pi (default: ~/rc_car_control/arduino_wasd_controller.py)"
    exit 1
fi

COMMAND="$1"

# Map 'space' to actual space character
if [ "$COMMAND" = "space" ] || [ "$COMMAND" = "stop" ]; then
    COMMAND=" "
fi

ssh "$PI_USER@$PI_HOST" "python3 $SCRIPT_PATH $COMMAND"

