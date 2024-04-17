#!/bin/bash

## Usage ##
# Download Latest Stable Build:
# curl -s https://raw.githubusercontent.com/djh20/volt/main/install.sh | sudo bash -s stable

# Download Latest Beta Build: 
# curl -s https://raw.githubusercontent.com/djh20/volt/main/install.sh | sudo bash -s beta

cd /tmp

URL="https://api.github.com/repos/djh20/volt/releases/latest"
RELEASE_TYPE="$1"

if [ "$RELEASE_TYPE" == "beta" ]; then
  URL="https://api.github.com/repos/djh20/volt/releases?per_page=1"
fi

curl -s "$URL" \
| grep "browser_download_url.*deb" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -O volt.deb -qi -

apt-get install -y ./volt.deb
rm volt.deb