#!/bin/sh

apt-get install python3.6 -y
python3.6 -m pip install --upgrade pip

cd /

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

python3.6 -m pip install -Ur requirements.txt
echo "Installed Python dependencies"

echo "Starting bot"
python3.6 bot.py &
