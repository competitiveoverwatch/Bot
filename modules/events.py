from config import const

import arrow
import requests
from modules.twitch import Twitch
from urllib.parse import urlparse

class Events:

    def __init__(self, logger):
        self.logger = logger
        self.twitch = Twitch(self.logger)

    def __get_events_json(self):
        query = "|".join([
            "[[Category:Tournaments]]",
            "[[Is tier::Premier||Major]]",
            "[[Has_end_date::>]]",
            "?Has_name",
            "?Has_tournament_twitch",
            "?Has_start_date",
            "?Has_end_date",
            "?Has_prize_pool",
            "offset=0",
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

    def __get_live_badge(self, twitch_url):
        channel_name = urlparse(twitch_url).path

        if len(channel_name) > 1:
            channel_name = channel_name[1:] # Remove preceding slash

            if self.twitch.is_channel_live(channel_name):
                return const.format_event_live

        return ""

    def __format_event_dates(self, has_start_date, has_end_date, liquipedia_url):
        # Convert to datetime
        start = arrow.get(has_start_date)
        end = arrow.get(has_end_date)

        now = arrow.utcnow()

        # If start == end, event may have been rescheduled/something else happened
        # e.g. this happened with Masters Gaming Arena 2016
        if start == end:
            return const.format_event_date_tba

        else:
            formatted_start = None
            if start <= now:
                formatted_start = const.format_event_date_started
            else:
                formatted_start = start.format(const.format_event_date)

            formatted_end = None
            # Check `start > now` to avoid "Ongoing – 31" or similar nonsense
            if (start.month == end.month) and start > now:
                formatted_end = end.format(const.format_event_date_same_month)
            else:
                formatted_end = end.format(const.format_event_date)

            return (const.format_event_date_line.format(formatted_start, formatted_end, liquipedia_url), end < now)

    def get_formatted(self, sidebar_length):
        data = self.__get_events_json()

        if data is None:
            return data

        else:
            results = data["query"]["results"]

            events = ""

            for event, details in results.items():
                printouts = details["printouts"]

                name = printouts["Has name"][0]
                liquipedia_url = details["fullurl"]
                twitch_url = printouts["Has tournament twitch"]

                if len(twitch_url) == 1:
                    twitch_url = twitch_url[0]
                else:
                    twitch_url = ""

                # Format start and end dates
                has_start_date = printouts["Has start date"][0]
                has_end_date = printouts["Has end date"][0]
                dates, has_ended = self.__format_event_dates(has_start_date, has_end_date, liquipedia_url)

                # Use Twitch URL for link (and check if live) if it exists
                # otherwise use the Liquipedia URL
                live_badge = ""
                if twitch_url == "":
                    twitch_url = liquipedia_url
                elif not has_ended:
                    live_badge = self.__get_live_badge(twitch_url)
                
                # Format prize pool
                prizepool = printouts["Has prize pool"]
                prizepool = prizepool[0] if (len(prizepool) == 1) else 0

                formatted_prizepool = ""
                if prizepool > 0:
                    # Round prizepool to nearest 10, add commas
                    prizepool = round(prizepool, -1)
                    formatted_prizepool = const.format_event_prizepool.format(prizepool)

                # Piece everything together into an event
                new_event = const.format_event.format(live_badge, name, twitch_url, formatted_prizepool, dates)

                if sidebar_length + len(events) + len(new_event) > const.sidebar_length_limit:
                    break

                else:
                    events += new_event
                    sidebar_length += len(new_event)

            return events