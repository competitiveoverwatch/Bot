from config import const, creds
import requests

class Twitch():
    __api_base = "https://api.twitch.tv/kraken/{}"

    __headers = {
        "Accept": "application/vnd.twitchtv.v5+json",
        "Client-ID": creds.twitch_client_id,
        "User-Agent": const.user_agent
    }

    @classmethod
    def __get(cls, path, *params):

        data = None

        url = Twitch.__api_base.format(path)

        try:
            if len(params) != 1 or params[0] == None:
                data = requests.get(url, headers = Twitch.__headers)
            else:
                data = requests.get(url, params = params[0], headers = Twitch.__headers)

            data.raise_for_status()
            data = data.json()
            return data

        except (HTTPError, ValueError) as e:
            print(e)
            return None

    @classmethod
    def __get_id(cls, channel_name):

        data = Twitch.__get("search/channels", {
            "query": channel_name,
            "limit": "1"
        })

        if data is not None:
            channels = data["channels"]
            if len(channels) == 0:
                print(f"Failed to get id for {channel_name}")
                return None

            else:
                id = channels[0]["_id"]
                return id

        else:
            return data # (None)
        
    @classmethod
    def is_channel_live(cls, channel_name):

        channel_id = Twitch.__get_id(channel_name)
        if channel_id is None:
            return False

        else:
            path = "streams/" + str(channel_id)
            data = Twitch.__get(path)

            return (data["stream"] != None)