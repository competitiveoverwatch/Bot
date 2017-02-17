from config import const, creds
import requests
from tinydb import TinyDB, Query
from urllib.parse import urlparse

import os, os.path
if not os.path.exists("db/"):
    os.makedirs("db/")

db = TinyDB("db/twitch.json")

class Twitch():
    __api_base = "https://api.twitch.tv/kraken/{}"

    __headers = {
        "Accept": "application/vnd.twitchtv.v5+json",
        "Client-ID": creds.twitch_client_id,
        "User-Agent": const.user_agent
    }

    __status_blacklist = ["rerun:","[rerun]","rebroadcast"]

    def __init__(self, logger):
        self.logger = logger

    def __get(self, path, *params):

        data = None

        url = self.__api_base.format(path)

        try:
            if len(params) != 1 or params[0] == None:
                data = requests.get(url, headers = self.__headers)
            else:
                data = requests.get(url, params = params[0], headers = self.__headers)

            data.raise_for_status()
            data = data.json()
            return data

        except (HTTPError, ValueError) as e:
            self.logger.exception(e)
            return None

    def __get_id(self, channel_name):

        Channel = Query()
        results = db.search(Channel.name == channel_name)
        if len(results) == 1:
            return results[0]["id"]

        else:
            data = self.__get("search/channels", {
                "query": channel_name,
                "limit": "1"
            })

            if data is not None:
                channels = data["channels"]
                if len(channels) == 0:
                    self.logger.error(f"Failed to get id for {channel_name}")
                    return None

                else:
                    id = channels[0]["_id"]

                    db.insert({"name": channel_name, "id": id})

                    return id

            else:
                return data # (None)

    def __get_channel_name(self, twitch_url):

        channel_name = urlparse(twitch_url).path

        if len(channel_name) > 1:
            return channel_name[1:] # Remove preceding slash

        return None

    def is_channel_live(self, twitch_url):

        channel_name = self.__get_channel_name(twitch_url)
        if channel_name is not None:

            channel_id = self.__get_id(channel_name)
            if channel_id is not None:

                path = "streams/" + str(channel_id)
                data = self.__get(path)

                stream = data["stream"]
                if stream is not None:
                    status = data["stream"]["channel"]["status"]

                    return (status is not None and not any(x in status.lower() for x in self.__status_blacklist))

        return False