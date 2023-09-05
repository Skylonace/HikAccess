#!/bin/sh

python3 "server.py" &
nginx -g "daemon off;error_log /dev/stdout debug;"