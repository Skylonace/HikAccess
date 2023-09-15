#!/usr/bin/with-contenv bashio

DEVICE_IP="$(bashio::config 'device_ip')"
export DEVICE_IP

nginx -g "daemon off;error_log /dev/stdout debug;" &
python3 "server.py"