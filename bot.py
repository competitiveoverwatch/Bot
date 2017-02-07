from config import const, creds

from modules.events import Events
from modules.megathreads import Megathreads
from modules.ScheduledThread import ScheduledThread
from modules.rules import Rule, Rules

import arrow
from dateutil import tz
import logging
from logging.handlers import RotatingFileHandler
import math
import praw
from praw.exceptions import APIException
import requests
import requests_cache
from threading import Event, Thread
import time
import tweepy

import os, os.path
if not os.path.exists("logs/"):
    os.makedirs("logs/")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("logs/bot.log", maxBytes=1024000, backupCount=5)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

cache_seconds = 60 * 4.5 # Cache for 4.5 minutes
sidebar_repeat_seconds = 60 * 5 # Update sidebar every 5 minutes
megathread_repeat_seconds = 60 * 60 # Post megathreads if necessary every hour

# Base class/superclass for all threads/bot modules
class BotThread(Thread):
    def __init__(self, subreddit, repeat_time):
        super().__init__()
        self.subreddit = subreddit
        self.repeat_time = repeat_time

    def run(self):

        if self.repeat_time > 0:

            while True:
                try:
                    self.main()

                except praw.exceptions.PRAWException as e:
                    logger.exception(e)

                    # If any Reddit error (e.g. down)
                    # try again after 30 seconds
                    time.sleep(30)
                    self.main()

                time.sleep(self.repeat_time)

        else:
            self.main()

    # Subclasses override
    def main(self):
        pass

# Updates sidebar text
class SidebarUpdaterThread(BotThread):

    def __init__(self, subreddit, repeat_time, twitter_api):
        super().__init__(subreddit, repeat_time)

        self.events = Events(logger)
        self.megathreads = Megathreads(logger, self.subreddit, twitter_api)

    def main(self):
        logger.info("SIDEBAR: Beginning update")

        sidebar_template = self.subreddit.wiki["sidebar_template"].content_md
        sidebar_length = len(sidebar_template)
        
        megathreads_str = self.megathreads.get_formatted_latest()
        events_str = self.events.get_formatted(sidebar_length)
        
        if megathreads_str is None or len(megathreads_str) == 0:
            logger.error("SIDEBAR: Failed to fetch megathreads")

        elif events_str is None or len(events_str) == 0:
            logger.error("SIDEBAR: Failed to fetch events")

        else:
            new_sidebar = sidebar_template.format(megathreads = megathreads_str, events = events_str)

            #print(new_sidebar)

            self.subreddit.mod.update(description = new_sidebar, key_color = const.key_color, spoilers_enabled = const.spoilers_enabled)

            logger.info("SIDEBAR: Successfully updated")

        logger.info(f"SIDEBAR: Next update in {sidebar_repeat_seconds}s")

# Moderates posts and comments
class ModerationThread(BotThread):

    def __init__(self, subreddit, repeat_time):
        super().__init__(subreddit, repeat_time)

        self.megathreads = Megathreads(logger, self.subreddit, None)
        self.rules = Rules(subreddit, self.megathreads)

    def __moderate_post(self, post):
        valid, rule = self.rules.validate_post(post)
        if not valid:

            formatted_rule = rule.formatted()
            if formatted_rule is not None:

                comment_text = f"\n{const.mod_removal_prefix}\n"
                for line in formatted_rule.split("\n"):
                    comment_text += f"\n> {line.strip()}"

                comment_text += f"\n\n{const.mod_removal_suffix}"

                logger.debug(f"MODERATOR: Removed '{post.title}' for: {rule.name}")

                comment = post.reply(comment_text)
                # If we fail to reply (e.g. post is archived etc.)
                # don't perform other actions either
                # (BotThread's `try: except:` will break here)

                comment.mod.distinguish(how = "yes", sticky = True)

            post.mod.remove()
            post.mod.flair() # Remove flair

    def __moderate_comment(self, comment, post):
        valid, rule = self.rules.validate_comment(comment)
        if not valid:

            if comment.parent_id == comment.link_id:
                logger.debug(f"MODERATOR: Removed root comment on '{post.title}' for: {rule.name}")
            else:
                logger.debug(f"MODERATOR: Removed comment reply on '{post.title}' for: {rule.name}")
            
            comment.mod.remove()

    def main(self):
        for post in self.subreddit.stream.submissions():
            self.__moderate_post(post)

            post.comments.replace_more(limit=0)
            for comment in post.comments.list():

                # If a comment has been removed, banned_by = username of mod that removed
                if comment.banned_by is None:
                    self.__moderate_comment(comment, post)

# Posts megathreads
class MegathreadPosterThread(BotThread):

    def __init__(self, subreddit, repeat_time):
        super().__init__(subreddit, repeat_time)
        self.megathreads = Megathreads(logger, self.subreddit, None)

    def main(self):
        sec_per_hour = 60*60
        sec_per_day = sec_per_hour * 24
        sec_per_week = sec_per_day * 7

        sec_time_tolerance = 20 * 60 # 20 minutes

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
                    logger.info(f"MEGATHREAD: Would post {thread.title} now")
                    self.megathreads.post(thread, now)

def authorise_twitter():
    auth = tweepy.OAuthHandler(creds.twitter_consumer_token, creds.twitter_consumer_secret)
    auth.set_access_token(creds.twitter_access_token, creds.twitter_access_token_secret)

    # At the moment, Twitter access tokens do not expire unless revoked.
    # The bot runs on a subreddit-owned Twitter account only, so we should
    # be fine to generate once, and stored permanently in `creds.py`.

    '''
    try:
        redirect_url = auth.get_authorization_url()
        print(f"Please visit {redirect_url} to authorise Twitter access.")

    except tweepy.TweepError:
        print("Error! Failed to get request token.")

    verifier = input("Verification Code: ")

    try:
        access_token, access_token_secret = auth.get_access_token(verifier)
        print(f"Access Token: {access_token}")
        print(f"Access Token Secret: {access_token_secret}")

    except tweepy.TweepError:
        print("Error! Failed to get access token.")
    '''

    return auth

def start_thread(class_name, subreddit, repeat_time):
    t = class_name(subreddit, repeat_time)
    t.daemon = True
    t.start()

def main():

    requests_cache.install_cache("db/requests_cache", expire_after = cache_seconds, old_data_on_error = True)

    reddit = praw.Reddit(client_id = creds.reddit_client_id,
                         client_secret = creds.reddit_client_secret,
                         password = creds.reddit_password,
                         user_agent = const.user_agent,
                         username = creds.reddit_username)

    subreddit = reddit.subreddit(const.subreddit)

    auth = authorise_twitter()
    twitter_api = tweepy.API(auth)

    sidebar_thread = SidebarUpdaterThread(subreddit, sidebar_repeat_seconds, twitter_api)
    sidebar_thread.daemon = True
    sidebar_thread.start()

    # Megathread scheduler + moderation run on test sub for now
    test_subreddit = reddit.subreddit("co_test")
    start_thread(MegathreadPosterThread, test_subreddit, megathread_repeat_seconds)
    start_thread(ModerationThread, test_subreddit, 0) # Doesn't need to repeat - constantly streams

    keep_alive_event = Event()
    keep_alive_event.wait()

main()