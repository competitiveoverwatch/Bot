import json
from collections import namedtuple

data = None

with open("config/config.json") as config_data:
    config_data = json.load(config_data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    with open("config/creds.json") as creds_data:
        creds = json.load(creds_data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

        data = config_data._replace(creds=creds)