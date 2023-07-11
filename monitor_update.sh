#!/bin/bash

# Check if the Python script is running
if ! pgrep -f "$HOME/env/bin/python3 /home/ubuntu/market_depth_gateway.py" > /dev/null; then
    echo "Python script is not running. Restarting..."
    ~/env/bin/python3 /home/ubuntu/market_depth_gateway.py >/dev/null 2>&1 &
else
    echo "Python script is running."
fi