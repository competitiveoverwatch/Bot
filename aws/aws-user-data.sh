#!/bin/bash

apt-get update -y
apt-get install python3-pip -y

#This is gross. `cloud-init` can't find `requests` by default (??)
#Must be something I'm missing
python3 -m pip install requests

# Use Felix Krull's deadsnakes PPA.
# python3.6 is in the universe repository for 16.10 not 16.04
add-apt-repository ppa:fkrull/deadsnakes -y
apt-get install python3.6 -y
apt-get upgrade -y
apt-get dist-upgrade -y

#Make user-data execute at boot
#http://stackoverflow.com/questions/6475374/how-do-i-make-cloud-init-startup-scripts-run-every-time-my-ec2-instance-boots#comment60017981_10455027
sed -i 's/scripts-user$/\[scripts-user, always\]/' /etc/cloud/cloud.cfg
echo "Set to execute user-data at instance boot"

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

chmod +x aws-setup.sh

echo "Executing setup"
./aws/aws-setup.sh