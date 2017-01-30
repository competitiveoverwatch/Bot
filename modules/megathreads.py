import arrow
from config import const
from modules.ScheduledThread import ScheduledThread

class Megathreads:

    def __init__(self, subreddit):
        self.subreddit = subreddit

    def get_formatted_latest(self):
        titles = ["LFG: Find Players & Teams", "Advice: Questions & VOD Reviews", "Discussion Megathread"]
        keywords = ["lfg", "advice", "daily discussion"]

        searchQuery = "flair:'megathread' author:'automoderator'"

        megathreads = ""

        for thread in self.subreddit.search(searchQuery, sort = "new", syntax = "cloudsearch", time_filter = "month", limit = 7):
            title = thread.title.lower()

            for index, keyword in enumerate(keywords):
                if keyword in title:
                    title = titles[index]

                    # Remove used keywords/titles
                    keywords.pop(index)
                    titles.pop(index)

                    megathreads += const.format_megathread.format(title, thread.url)

        return megathreads

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
                raise ValueError("Invalid schedule thread")

        else:
            raise TypeError("Wrong argument type for `post(scheduled_thread)` (expected ScheduledThread)")