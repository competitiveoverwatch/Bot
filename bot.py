import const
import credentials

import events
import megathreads

import requests
import requests_cache

import praw

def update_sidebar(subreddit, sidebar_length):
    
    #megathreads_str = get_megathreads(subreddit)
    events_str = events.get(sidebar_length)
    print(events_str)
    
    '''
    sidebar_template = subreddit.wiki["sidebar_template"].content_md

    print("sidebar template: ", sidebar_template)

    sidebar = subreddit.mod.settings()["description"]
    print(sidebar)
    '''

def main():
    cache_seconds = 60 * 4.5 # Cache for 4.5 minutes
    requests_cache.install_cache(expire_after = cache_seconds, old_data_on_error = True)

    reddit = praw.Reddit(client_id = credentials.client_id,
                         client_secret = credentials.client_secret,
                         password = credentials.password,
                         user_agent = const.user_agent,
                         username = credentials.username)

    subreddit = reddit.subreddit(const.subreddit)

    sidebar_template = subreddit.wiki["sidebar_template"].content_md
    sidebar_length = len(sidebar_template)

    update_sidebar(subreddit, sidebar_length)

main()