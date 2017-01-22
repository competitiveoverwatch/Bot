from config import const, creds

from modules import events, megathreads

import requests
import requests_cache

import praw

from threading import Event, Thread
import time

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

    def main(self):
        print("\nSIDEBAR: Beginning update")

        sidebar_template = self.subreddit.wiki["sidebar_template"].content_md
        sidebar_length = len(sidebar_template)
        
        megathreads_str = megathreads.get_formatted_latest(self.subreddit)
        events_str = events.get_formatted(sidebar_length)

        if megathreads_str is None:
            print("SIDEBAR: Failed to fetch megathreads")

        elif events_str is None:
            print("SIDEBAR: Failed to fetch events")

        else:
            new_sidebar = sidebar_template.replace(const.sidebar_replacement_megathreads, megathreads_str)
            new_sidebar = new_sidebar.replace(const.sidebar_replacement_events, events_str)

            #print(new_sidebar)

            self.subreddit.mod.update(description = new_sidebar, key_color = const.key_color, spoilers_enabled = const.spoilers_enabled)

            print("SIDEBAR: Successfully updated")

        print(f"SIDEBAR: Completed update. Next update in {sidebar_repeat_seconds} seconds")

class ModerationThread(BotThread):

    def main(self):
        pass

class MegathreadSchedulerThread(BotThread):

    def main(self):
        pass

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

    keep_alive_event = Event()
    keep_alive_event.wait()

main()