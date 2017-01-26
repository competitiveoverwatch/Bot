from config import const
from modules import ScheduledThread

class Megathreads:

    def __init__(self, subreddit):
        self.subreddit = subreddit

    def get_formatted_latest(self):
        titles = ["LFG: Find Players & Teams", "Advice: Questions & VOD Reviews", "Discussion Megathread", "Balance & Meta Megathread"]
        keywords = ["lfg", "advice", "daily discussion", "balance"]

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

    def post(self, scheduled_thread):
        if isinstance(scheduled_thread, ScheduledThread):

            if scheduled_thread.is_valid():
                submission = self/subreddit.submit(scheduled_thread.title, selftext = scheduled_thread.text, send_replies = False)

                # TODO: Test how flair choices work
                # choices = submission.flair.choices()
                # template_id = next(x for x in choices
                #                    if x['flair_text_editable'])['flair_template_id']
                # submission.flair.select(template_id)

            else:
                raise ValueError("Invalid schedule thread")

        else:
            raise TypeError("Wrong argument type for `post(scheduled_thread)` (expected ScheduledThread)")