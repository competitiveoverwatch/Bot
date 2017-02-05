from config import const

import arrow
import requests
from modules.twitch import Twitch
from operator import attrgetter

class Event:

    def __init__(self, event_printouts_json, twitch):
        self.__twitch = twitch
        self.__parse_json(event_printouts_json)

    def has_ended(self):
        return self.end.replace(hours=+24) < arrow.utcnow()

    def __parse_json(self, event_printouts_json):
        printouts = event_printouts_json["printouts"]

        self.name = printouts["Has name"][0]
        self.liquipedia_url = event_printouts_json["fullurl"]

        self.start = arrow.get(printouts["Has start date"][0])
        self.end = arrow.get(printouts["Has end date"][0])

        # Use Twitch URL for link (and check if live) if it exists
        # otherwise use the Liquipedia URL
        twitch_url = printouts["Has tournament twitch"]
        if len(twitch_url) == 1:
            self.twitch_url = twitch_url[0]
        else:
            self.twitch_url = None

        prizepool = printouts["Has prize pool"]
        self.prizepool = prizepool[0] if (len(prizepool) == 1) else 0

        self.cached_live = self.is_live()

    def is_live(self):
        return (not self.has_ended() and self.twitch_url is not None and self.__twitch.is_channel_live(self.twitch_url))

    def __format_dates(self):
        now = arrow.utcnow()

        # If start == end, event may have been rescheduled/something else happened
        # e.g. this happened with Masters Gaming Arena 2016
        if self.start == self.end:
            return const.format_event_date_tba

        else:
            formatted_start = None
            if self.start <= now:
                formatted_start = const.format_event_date_started
            else:
                formatted_start = self.start.format(const.format_event_date)

            formatted_end = None
            # Check `start > now` to avoid "Ongoing – 31" or similar nonsense
            if (self.start.month == self.end.month) and self.start > now:
                formatted_end = self.end.format(const.format_event_date_same_month)
            else:
                formatted_end = self.end.format(const.format_event_date)

            return const.format_event_date_line.format(start = formatted_start, end = formatted_end, liquipedia_url = self.liquipedia_url)

    def formatted(self):
        live_badge = ""
        if self.is_live():
            live_badge = const.format_event_live

        url = self.liquipedia_url if (self.twitch_url is None) else self.twitch_url

        formatted_prizepool = ""
        if self.prizepool > 0:
            # Round prizepool to nearest 10, add commas
            rounded_prizepool = round(self.prizepool, -1)
            formatted_prizepool = const.format_event_prizepool.format(rounded_prizepool)

        formatted_dates = self.__format_dates()

        return const.format_event.format(live_badge = live_badge, name = self.name, url = url, prizepool = formatted_prizepool, dates = formatted_dates)

class Events:

    def __init__(self, logger):
        self.logger = logger
        self.twitch = Twitch(self.logger)

    def __get_events_json(self):

        yesterday = arrow.get().replace(days=-1).format("YYYY-MM-DD")

        query = "|".join([
            "[[Category:Tournaments]]",
            "[[Is tier::Premier||Major]]",
            "[[Has_end_date::>" + yesterday + "]]",
            "?Has_name",
            "?Has_tournament_twitch",
            "?Has_start_date",
            "?Has_end_date",
            "?Has_prize_pool",
            "limit=6",
            "sort=Has_start_date",
            "order=asc"
        ])

        payload = {
            "action": "ask",
            "query": query,
            "format": "json"
        }

        headers = {
            "User-Agent": const.user_agent
        }

        url = "http://wiki.teamliquid.net/overwatch/api.php"

        try:
            data = requests.get(url, params = payload, headers = headers)
            data.raise_for_status()
            data = data.json()
            return data

        except (HTTPError, ValueError) as e:
            self.logger.exception(e)
            return None

    def get_formatted(self, sidebar_length):
        data = self.__get_events_json()

        if data is None:
            return data

        else:
            results = data["query"]["results"]

            sidebar_events = []

            # Create `Event` for each JSON object
            for event_key, event_printouts_json in results.items():
                new_event = Event(event_printouts_json, self.twitch)
                sidebar_events.append(new_event)

            # Sort live events first
            sidebar_events.sort(key = attrgetter("cached_live"), reverse = True)

            # Format actual sidebar text
            sidebar_text = ""

            for event in sidebar_events:
                new_event_text = event.formatted()
                new_event_text_len = len(new_event_text)

                if (sidebar_length + len(sidebar_text) + new_event_text_len) > const.sidebar_length_limit:
                    break

                else:
                    sidebar_text += new_event_text
                    sidebar_length += new_event_text_len

            return sidebar_text