import const

def get_megathreads(subreddit):
    titles = ["LFG: Find Players & Teams", "Advice: Questions & VOD Reviews", "Daily Balance & Meta Megathread"]
    keywords = ["lfg", "advice", "discussion"]

    searchQuery = "flair:'megathread' author:'automoderator'"

    megathreads = ""

    for thread in subreddit.search(searchQuery, sort = "new", syntax = "cloudsearch", time_filter = "month", limit = 4):
        title = thread.title.lower()

        for index, keyword in enumerate(keywords):
            if keyword in title:
                title = titles[index]

                # Remove used keywords/titles
                keywords.pop(index)
                titles.pop(index)

                megathreads += const.format_megathread.format(title, thread.url)

    return megathreads