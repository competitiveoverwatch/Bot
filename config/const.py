subreddit = "CompetitiveOverwatch"
key_color = "#545452" # Reddit's "dark grey"
spoilers_enabled = True

user_agent = f"r/{subreddit} sidebar updater. (Contact us via r/{subreddit} modmail)"

# Doubled from 5,120 to 10,240 in August '16
# https://www.reddit.com/r/changelog/comments/4x91ql/reddit_change_updates_to_the_sidebar/
sidebar_length_limit = 10_240

### Moderation
mod_removal_prefix = f"Thank you for your submission to /r/{subreddit}! Unfortunately, it was removed for the following reason:"
mod_removal_suffix = f"Please [message the moderators](https://www.reddit.com/message/compose?to=%2Fr%2F{subreddit}) if you have any questions."

mod_lfg_removal_description = """LFG/LFT and related posts are not allowed as individual text posts on the subreddit.
\nTo prevent the subreddit from being spammed with posts of players looking for teams or teammates, the subreddit 
runs a [**weekly thread**]({lfg_megathread_url}) which can be found in the banner. 
Please direct posts to that thread, /r/OverwatchLFT, or use external websites. Thanks!"""

### Sidebar formatting
sidebar_replacement_megathreads = "{megathreads}"
sidebar_replacement_events = "{events}"

## Megathreads
megathreads = [
    {
        "keyword": "lfg",
        "title": "LFG: Find Players & Teams",
        "tweet": "Looking for people or teams to play with? Recruiting? Check out our weekly #Overwatch LFG megathread! {url}"
    },
    {
        "keyword": "advice",
        "title": "Advice: Questions & VOD Reviews",
        "tweet": "Got questions? Need gameplay reviewed? This week's Advice Megathread is the place: {url} #Overwatch",
    },
    {
        "keyword": "weekly discussion",
        "title": "Discussion Megathread",
        "tweet": "This week's Discussion Megathread: {url} #Overwatch"
    }
]


format_megathread = "> [{title}]({url})\n"

## Event
format_event = "####[{live_badge}{name}]({url}){prizepool}\n\n{dates}\n\n"

format_event_live = "**LIVE:** "

# Add commas to prizepool integer
format_event_prizepool = "\n\n${:,} Prize Pool"

# Event dates
format_event_date_line = "[**{start} – {end}**]({liquipedia_url})"

format_event_date_tba = "Dates TBA"
format_event_date_started = "Ongoing"
format_event_date_same_month = "D"
format_event_date = "MMMM D"