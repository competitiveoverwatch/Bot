#!/bin/bash
apt-get upgrade -y

#Install pip as it does not appear to be installed with python for some reason
if ! test -f get-pip.py
then
	wget https://bootstrap.pypa.io/get-pip.py
	python3.6 get-pip.py
	rm get-pip.py
fi

echo "Installed pip, updated and upgraded"

pip install --upgrade awscli -q

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

rm -rf AWS
rm README.md
rm LICENSE
rm config/creds.template.py

#Download creds
cd config
aws s3 cp s3://r-competitiveoverwatch/creds.py . --region us-east-1
echo "Downloaded creds.py"

#Go back to bot directory
cd ../

python3.6 -m pip install -U -r requirements.txt
echo "Installed Python dependencies"

python3.6 bot.py