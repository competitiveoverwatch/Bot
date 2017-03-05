#!/bin/bash

apt-get update -y
apt-get install python3-pip -y

# Use Felix Krull's deadsnakes PPA.
# python3.6 is in the universe repository for 16.10 not 16.04
add-apt-repository ppa:fkrull/deadsnakes -y
apt-get install python3.6 -y
apt-get upgrade -y
apt-get dist-upgrade -y

cd /home/ubuntu

#Update or clone
if test -d bot
then
	cd bot
	git pull
	echo "Updated bot"
else
	git clone https://github.com/sebj/r-CompetitiveOverwatch-Bot bot -b master
	cd bot
	echo "Cloned bot"
fi

chmod +x digitalocean/setup.sh

echo "Executing setup"
./digitalocean/setup.sh