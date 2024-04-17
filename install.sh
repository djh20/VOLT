#!/bin/bash
# Usage: curl https://raw.githubusercontent.com/djh20/volt/main/install.sh | sudo bash

cd /tmp

curl -s https://api.github.com/repos/djh20/volt/releases/latest \
| grep "browser_download_url.*deb" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -O volt-latest.deb -qi -

apt-get install ./volt-latest.deb
rm volt-latest.deb