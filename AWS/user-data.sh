#!/bin/bash

# Use Felix Krull's deadsnakes PPA.
# python3.6 is in the universe repository for 16.10 not 16.04
add-apt-repository ppa:fkrull/deadsnakes -y
apt-get update -y
apt-get install python3.6 -y
apt-get install awscli -y

#Make user-data execute at boot
#http://stackoverflow.com/questions/6475374/how-do-i-make-cloud-init-startup-scripts-run-every-time-my-ec2-instance-boots#comment60017981_10455027
sed -i 's/scripts-user$/\[scripts-user, always\]/' /etc/cloud/cloud.cfg
echo "Set to execute user-data at instance boot"

cd /home/ubuntu