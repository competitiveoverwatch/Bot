#!/bin/bash

# Use Felix Krull's deadsnakes PPA.
# python3.6 is in the universe repository for 16.10 not 16.04
add-apt-repository ppa:fkrull/deadsnakes -y
apt-get update -y
apt-get install python3.6 -y
apt-get install awscli -y
apt-get upgrade -y

#Make user-data execute at boot
#http://stackoverflow.com/questions/6475374/how-do-i-make-cloud-init-startup-scripts-run-every-time-my-ec2-instance-boots#comment60017981_10455027
sed -i 's/scripts-user$/\[scripts-user, always\]/' /etc/cloud/cloud.cfg
echo "Set to execute user-data at instance boot"

cd /home/ubuntu

#Install pip as it does not appear to be installed with python for some reason
if ! test -f get-pip.py
then
	wget https://bootstrap.pypa.io/get-pip.py
	python3.6 get-pip.py
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

python3.6 -m pip install -U -r requirements.txt -q
echo "Installed Python dependencies"

touch user-data-ran.test

screen -S bot python3.6 bot.py