#!/bin/bash

if [ -d "/opt/Hardcode-Tray" ];then
  sudo rm -rf /opt/Hardcode-Tray
fi
if [ -L "/usr/bin/hardcode-tray" ];then
  sudo rm -f /usr/bin/hardcode-tray
fi
