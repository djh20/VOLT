#!/bin/bash
# Usage: curl https://raw.githubusercontent.com/djh20/volt/main/install.sh | sudo bash

curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

apt-get update
apt-get install -y redis

cd /tmp

curl -s https://api.github.com/repos/djh20/volt/releases/latest \
| grep "browser_download_url.*deb" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -O volt-latest.deb -qi -

apt-get install ./volt-latest.deb
rm volt-latest.deb