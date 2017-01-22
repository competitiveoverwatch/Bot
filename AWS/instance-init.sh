#!/bin/bash
apt-get upgrade -y

#Install pip as it does not appear to be installed with python for some reason
if ! test -f get-pip.py
then
	wget https://bootstrap.pypa.io/get-pip.py
	python3.6 get-pip.py
	shred -u get-pip.py
fi

echo "Installed dependencies, updated and upgraded"

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

#Go back to bot directory
cd ../

python3.6 -m pip install -U -r requirements.txt
echo "Installed Python dependencies"

python3.6 run.py