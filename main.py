import constants
import credentials
import praw
import requests
from twitch.api import v3

def stream_live(channel_name):
    pass

def get_megathreads(subreddit):
    titles = ["LFG: Find Players & Teams", "Advice: Questions & VOD Reviews", "Daily Balance & Meta Megathread"]
    keywords = ["lfg", "advice", "discussion"]

    searchQuery = "flair:'megathread' author:'automoderator'"

    megathreads = ""

    for thread in subreddit.search(searchQuery, sort="new", syntax="cloudsearch", time_filter="month", limit=4):
        title = thread.title.lower()

        for index, keyword in enumerate(keywords):
            if keyword in title:
                title = titles[index]

                keywords.pop(index)
                titles.pop(index)

                megathreads += constants.format_megathread.format(title, thread.url)

    return megathreads

def get_events():
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
        "User-Agent": constants.user_agent
    }

    url = "http://wiki.teamliquid.net/overwatch/api.php?"

    data = requests.get(url, params=payload, headers=headers)
    
    # TODO: Raises ValueError if response cannot be decoded - handle
    data = data.json()

    results = data["query"][results]

    #for event in results:


    print(results) 

def main():
    reddit = praw.Reddit(client_id = credentials.client_id,
                         client_secret = credentials.client_secret,
                         password = credentials.password,
                         user_agent = credentials.user_agent,
                         username = credentials.username)

    subreddit = reddit.subreddit(constants.subreddit)

    print(reddit.user.me())

    #megathreads = get_megathreads(subreddit)
    #get_events()

    '''
    sidebar_template = subreddit.wiki["sidebar_template"].content_md

    print("sidebar template: ", sidebar_template)

    sidebar = subreddit.mod.settings()["description"]
    print(sidebar)
    '''

main()