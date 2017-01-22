from config import const

import datetime
import requests
from modules.twitch import Twitch
from urllib.parse import urlparse

def __get_events_json():
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
        print(e)
        return None

def __get_live_badge(twitch_url):
    channel_name = urlparse(twitch_url).path

    if len(channel_name) > 1:
        channel_name = channel_name[1:] # Remove preceding slash

        if Twitch.is_channel_live(channel_name):
            return const.format_event_live

    return ""

def __format_event_dates(has_start_date, has_end_date):
    start_timestamp = float(has_start_date)
    end_timestamp = float(has_end_date)

    # Convert to datetime
    start = datetime.datetime.fromtimestamp(start_timestamp)
    end = datetime.datetime.fromtimestamp(end_timestamp)

    now = datetime.datetime.utcnow()

    # If start == end, event may have been rescheduled/something else happened
    # e.g. this happened with Masters Gaming Arena 2016
    if start_timestamp == end_timestamp:
        return const.format_event_date_tba

    else:
        formatted_start = None
        if start <= now:
            formatted_start = const.format_event_date_started
        else:
            formatted_start = start.strftime(const.format_event_date)

        formatted_end = None
        # Check `start > now` to avoid "Ongoing – 31" or similar nonsense
        if (start.month == end.month) and start > now:
            formatted_end = end.strftime(const.format_event_date_same_month)
        else:
            formatted_end = end.strftime(const.format_event_date)

        return const.format_event_date_line.format(formatted_start, formatted_end)

def get_formatted(sidebar_length):
    data = __get_events_json()

    if data is None:
        return data

    else:
        results = data["query"]["results"]

        events = ""

        for event, details in results.items():
            printouts = details["printouts"]

            name = printouts["Has name"][0]
            twitch_url = printouts["Has tournament twitch"][0]

            # Use Twitch URL for link (and check if live) if it exists
            # otherwise use the Liquipedia URL
            live_badge = ""
            if twitch_url == "":
                twitch_url = details["fullurl"]

            else:
                live_badge = __get_live_badge(twitch_url)

            # Format start and end dates
            has_start_date = printouts["Has start date"][0]
            has_end_date = printouts["Has end date"][0]
            dates = __format_event_dates(has_start_date, has_end_date)
            
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