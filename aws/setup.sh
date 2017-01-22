if ! test -f /usr/local/bin/pip
then
	wget https://bootstrap.pypa.io/get-pip.py
	python3.6 get-pip.py
fi

echo "Installed pip, updated and upgraded"

rm README.md
rm LICENSE
rm config/creds.template.py

#Download creds
cd config
aws s3 cp s3://r-competitiveoverwatch/creds.py . --region us-east-1
echo "Downloaded creds.py"

#Go back to bot directory
cd ../

pip install -U -r requirements.txt
echo "Installed Python dependencies"

python3.6 bot.py