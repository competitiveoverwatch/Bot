from config import const, creds

from modules.events import Events
from modules.megathreads import Megathreads
from modules.ScheduledThread import ScheduledThread
from modules.rules import Rules

import arrow
from dateutil import tz
import logging
from logging.handlers import RotatingFileHandler
import math
import praw
import requests
import requests_cache
from threading import Event, Thread
import time

import os, os.path
if not os.path.exists("logs/"):
    os.makedirs("logs/")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/bot.log", maxBytes=1024000, backupCount=5)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

cache_seconds = 60 * 4.5 # Cache for 4.5 minutes
sidebar_repeat_seconds = 60 * 5 # Update sidebar every 5 minutes
megathread_repeat_seconds = 60 * 60 # Post megathreads if necessary every hour

class BotThread(Thread):
    def __init__(self, subreddit, repeat_time):
        super().__init__()
        self.subreddit = subreddit
        self.repeat_time = repeat_time

    def run(self):
        while True:
            self.main()
            time.sleep(self.repeat_time)

    # Subclasses override
    def main(self):
        pass

class SidebarThread(BotThread):

    def __init__(self, subreddit, repeat_time):
        super().__init__(subreddit, repeat_time)
        self.events = Events(logger)
        self.megathreads = Megathreads(self.subreddit)

    def main(self):
        logger.info("SIDEBAR: Beginning update")

        sidebar_template = self.subreddit.wiki["sidebar_template"].content_md
        sidebar_length = len(sidebar_template)
        
        megathreads_str = self.megathreads.get_formatted_latest()
        events_str = self.events.get_formatted(sidebar_length)

        if megathreads_str is None:
            logger.error("SIDEBAR: Failed to fetch megathreads")

        elif events_str is None:
            logger.error("SIDEBAR: Failed to fetch events")

        else:
            new_sidebar = sidebar_template.replace(const.sidebar_replacement_megathreads, megathreads_str)
            new_sidebar = new_sidebar.replace(const.sidebar_replacement_events, events_str)

            #print(new_sidebar)

            self.subreddit.mod.update(description = new_sidebar, key_color = const.key_color, spoilers_enabled = const.spoilers_enabled)

            logger.info("SIDEBAR: Successfully updated")

        logger.info(f"SIDEBAR: Completed update. Next update in {sidebar_repeat_seconds} seconds")

class ModerationThread(BotThread):

    def main(self):
        pass
        #for submission in self.subreddit.stream.submissions():
            #Do something for each submission

class MegathreadSchedulerThread(BotThread):

    def main(self):
        sec_per_hour = 60*60
        sec_per_day = sec_per_hour * 24
        sec_per_week = sec_per_day * 7

        sec_time_tolerance = 5 * 60 # 5 minutes

        schedule = self.subreddit.wiki["automoderator-schedule"].content_md
        raw_threads = schedule.split("---")[1:] # Ignore first

        now = arrow.utcnow().timestamp

        for raw_thread in raw_threads:
            thread = ScheduledThread(raw_thread)

            if thread.is_valid():

                first_timestamp = thread.first.timestamp
                rounded_time_diff = None

                if thread.repeat_timespan == "hour":
                    rounded_time_diff = math.floor(((now - first_timestamp) / sec_per_hour) + 1) * sec_per_hour

                elif thread.repeat_timespan == "day":
                    rounded_time_diff = math.floor(((now - first_timestamp) / sec_per_day + 1)) * sec_per_day

                elif thread.repeat_timespan == "week":
                    rounded_time_diff = math.floor(((now - first_timestamp) / sec_per_week) + 1) * sec_per_week

                next_post = first_timestamp + rounded_time_diff

                if rounded_time_diff is not None and (next_post > now - sec_time_tolerance) and (next_post < now + sec_time_tolerance):
                    logger.info(f"{thread.title} would be posted now")

                    title = thread.title

                    # Temporary until we switch from AutoMod to OmnicOverlord
                    title = title.replace("%B %d", arrow.get(now).format("MMMM D"))

                    #self.subreddit.submit(title, selftext=thread.text, send_replies=False)

def start_thread(class_name, subreddit, repeat_time):
    t = class_name(subreddit, repeat_time)
    t.daemon = True
    t.start()

def main():

    requests_cache.install_cache(expire_after = cache_seconds, old_data_on_error = True)

    reddit = praw.Reddit(client_id = creds.client_id,
                         client_secret = creds.client_secret,
                         password = creds.password,
                         user_agent = const.user_agent,
                         username = creds.username)

    subreddit = reddit.subreddit(const.subreddit)

    #start_thread(ModerationThread, subreddit, )
    start_thread(SidebarThread, subreddit, sidebar_repeat_seconds)
    start_thread(MegathreadSchedulerThread, subreddit, megathread_repeat_seconds)

    keep_alive_event = Event()
    keep_alive_event.wait()

main()