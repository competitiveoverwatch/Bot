import arrow
from config import const
from tinydb import TinyDB, Query
import tweepy
from modules.ScheduledThread import ScheduledThread

import os, os.path
if not os.path.exists("db/"):
    os.makedirs("db/")

db = TinyDB("db/megathreads.json")

class Megathreads:

    def __init__(self, logger, subreddit, twitter_api):
        self.logger = logger
        self.subreddit = subreddit
        self.twitter_api = twitter_api

    @classmethod
    def is_valid_megathread(cls, megathread_date):
        return Megathreads.days_difference(arrow.utcnow(), arrow.get(megathread_date)) < 7

    @classmethod
    def is_expired_megathread(cls, megathread_date):
        return not Megathreads.is_valid_megathread(megathread_date)

    @classmethod
    def days_difference(cls, date1, date2):
        return abs(date1.timestamp - date2.timestamp) / (60*60*24)

    def tweet_megathread(self, index, url):

        if self.twitter_api is not None and not const.DEBUG:
            tweet_text = const.megathreads[index]["tweet"].format(url = url)
            self.twitter_api.update_status(tweet_text)

    # Returns an array of dictionaries (one for each megathread)
    # Megathread dictionary: {"title": "", "url": ""}
    def get_latest(self):

        # Remove old megathreads
        Megathread = Query()
        db.remove(Megathread.date.test(Megathreads.is_expired_megathread))

        keywords = []
        titles = []
        for m in const.megathreads:
            keywords.append(m["keyword"])
            titles.append(m["title"])

        latest_megathreads = []

        # Loop through valid megathreads, appending to array
        db_megathreads = db.all()
        for megathread in db_megathreads:

            title = megathread["title"]
            title_lower = title.lower()

            for index, keyword in enumerate(keywords):
                if keyword in title_lower:

                    latest_megathreads.append({"title": title, "url": megathread["url"]})

                    # Remove used keywords/titles
                    keywords.pop(index)
                    titles.pop(index)

        # If we removed any old megathreads earlier,
        # find the latest megathread links to fill gaps
        if len(keywords) > 0:

            for index, keyword in enumerate(keywords):
                query = f"flair:'megathread' author:'automoderator' title:\"{keyword}\""
                search = self.subreddit.search(query, sort = "new", syntax = "cloudsearch", time_filter = "month", limit = 1)
                
                for thread in search:
                    title = titles[index]
                    url = thread.url

                    date = arrow.get(thread.created)
                    formatted_date = date.format("YYYY-MM-DD")

                    db.insert({"title": title, "url": url, "date": formatted_date})

                    latest_megathreads.append({"title": title, "url": url})

                    # In future, tweet when posting megathread instead
                    if Megathreads.days_difference(arrow.utcnow(), date) < 1:
                        self.tweet_megathread(index, url)

                    keywords.pop(index)
                    titles.pop(index)

        return latest_megathreads

    def get_formatted_latest(self):

        megathreads_str = ""

        for megathread in self.get_latest():
            megathreads_str += const.format_megathread.format(title = megathread["title"], url = megathread["url"])

        return megathreads_str

    def post(self, scheduled_thread, now_timestamp):
        if isinstance(scheduled_thread, ScheduledThread):

            if scheduled_thread.is_valid():

                title = scheduled_thread.title

                # Temporary until we switch from AutoMod to OmnicOverlord
                title = title.replace("{{date %B %d}}", arrow.get(now_timestamp).format("MMMM D"))

                submission = self.subreddit.submit(title, selftext = scheduled_thread.text, send_replies = False)

                choices = submission.flair.choices()
                template_id = next(x for x in choices
                    if x["flair_css_class"] == "Megathread")["flair_template_id"]
                submission.flair.select(template_id)

                submission.mod.approve()
                submission.mod.suggested_sort(sort = "new")
                submission.mod.distinguish(how = "yes")

            else:
                logger.error("Attempted to post invalid scheduled thread")

        else:
            logger.error("Wrong argument type for `post(scheduled_thread)` (expected ScheduledThread)")