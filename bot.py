import const
import credentials

import events
import megathreads

import requests
import requests_cache

import praw

import threading

cache_seconds = 60 * 4.5 # Cache for 4.5 minutes
sidebar_update_seconds = 60 * 5 # Update sidebar every 5 minutes

def update_sidebar(subreddit):

    print("\nSIDEBAR: Beginning update")

    sidebar_template = subreddit.wiki["sidebar_template"].content_md
    sidebar_length = len(sidebar_template)
    
    megathreads_str = megathreads.get_formatted_latest(subreddit)
    events_str = events.get_formatted(sidebar_length)

    if megathreads_str is None:
        print("SIDEBAR: Failed to fetch megathreads")

    elif events_str is None:
        print("SIDEBAR: Failed to fetch events")

    else:
        new_sidebar = sidebar_template.replace(const.sidebar_replacement_megathreads, megathreads_str)
        new_sidebar = new_sidebar.replace(const.sidebar_replacement_events, events_str)

        subreddit.mod.update(description = new_sidebar, key_color = const.key_color, spoilers_enabled = const.spoilers_enabled)

        print("SIDEBAR: Successfully updated")

    print("SIDEBAR: Completed update")

def main():
    requests_cache.install_cache(expire_after = cache_seconds, old_data_on_error = True)

    reddit = praw.Reddit(client_id = credentials.client_id,
                         client_secret = credentials.client_secret,
                         password = credentials.password,
                         user_agent = const.user_agent,
                         username = credentials.username)

    subreddit = reddit.subreddit(const.subreddit)

    update_sidebar(subreddit)

    sidebar_timer = threading.Timer(sidebar_update_seconds, update_sidebar, [subreddit])
    sidebar_timer.start()

main()