#!/bin/bash

# Check if the Python script is running
if ! pgrep -f "~/env/bin/python3 /home/ubuntu/market_depth_gateway.py" > /dev/null; then
    echo "Python script is not running. Restarting..."
    ~/env/bin/python3 /home/ubuntu/market_depth_gateway.py >/dev/null 2>&1 &
else
    echo "Python script is running."
fi

try this instead

#!/bin/bash

. /etc/profile
export PATH=$PATH:/usr/bin

# Check if the Python script is running
if ! pgrep -f "~/env/bin/python3 /home/ubuntu/streaming_ec2.py" > /dev/null; then
        echo "Python script is not running. Restarting..."
        ~/env/bin/python3 /home/ubuntu/streaming_ec2.py >/dev/null 2>&1 &
else
        echo "Python script is running."
fi