if ! test -f /usr/local/bin/pip
then
	wget https://bootstrap.pypa.io/get-pip.py
	python3.6 get-pip.py
fi

echo "Installed pip, updated and upgraded"

pip install -Ur requirements.txt
echo "Installed Python dependencies"

echo "Starting bot"
python3.6 bot.py &