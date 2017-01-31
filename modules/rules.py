import praw

blacklist = ["MRW ","MFW ","[rant]","retard","cunt","kys","kill yourself","why the hell","why are you able to","sick and tired",
"fuck","console fags","you retarded","you're a fucking","nigger","suck dick","autism","fag","fuck that country"]

class Rule():
    def __init__(self, number, name, description):
        self.number = number
        self.posts = True
        self.comments = True
        self.name = name
        self.description = description

    def valid_post(self, post):
        pass

    def valid_comment(self, comment):
        pass

class SilentRule(Rule):

    def __init__(self):
        super().__init__(0, None, None)

    def valid_post(self, post):
        return (post.author.comment_karma > -90 and not "elo hell" in post.title.lower())

    def valid_comment(self, comment):
        return (comment.author.comment_karma > -90)

class BehaviorRule(Rule):
    def __init__(self):
        super().__init__(1, "No Poor or Abusive Behavior", """Posts and comments that are toxic or break Reddiquette will be removed. This includes, but is not limited to:
 
* Personal attacks and hateful language
* Witch-hunts and vote brigading
* Posting other users' personal information without consent (doxing)
* Offering, requesting, or linking to cheats, rank manipulation, or game-breaking exploits
 
If you see doxing, [message the mod team](https://www.reddit.com/message/compose?to=%2Fr%2FCompetitiveoverwatch) immediately.""")

    def valid_post(self, post):
        title = post.title.lower()

        if any(phrase in title for phrase in blacklist):
            return False

        return True

    def valid_comment(self, comment):

        if any(phrase in comment.body for phrase in blacklist):
            return False

        return True

class OffTopicLowEffortRule(Rule):
    def __init__(self):
        super().__init__(2, "No Off-Topic or Low-effort Content", """Off-topic and low-effort content can flood the subreddit and drown out meaningful discussion. As such, it is prohibited. This includes, but is not limited to:

* Posts not related to competitive mode / Overwatch esports
* Non-constructive complaints / rants 
* Screenshots / Highlight Videos / Gifs (see Rule 8)
* General gameplay videos
* Re-posted / repetitive content (please search before you post)
 
Post smaller questions in the Weekly Discussion Megathread (right side of the header).""" )
        self.comments = False

    def valid_post(self, post):
        title = post.title.lower()

        if len(title) < 5:
            return False

        if len(post.selftext) < 12 and post.is_self:
            return False

        return True

    def valid_comment(self, comment):

        tags = ["#check-yes","#check-no","#team-","#map-","#hero-"]

        # Remove root comments under 5 characters in length.
        # Leave root comments with image tags, because we don't know context (might be ok)
        if comment.is_root and len(comment.body) < 5 and not any(tag in comment.body for tag in tags):
            # Allow short replies to top-level comments,
            # but not top-level comments themselves
            return False


        if any(phrase in comment.body for phrase in blacklist):
            return False

        return True

class LFGRule(Rule):
    def __init__(self):
        super().__init__(0, None, """LFG/LFT and related posts are not allowed as individual text posts on the subreddit.

            To prevent the subreddit from being spammed with posts of players looking for teams or teammates, the subreddit runs a **weekly thread (the LFG Megathread)** which can be found in the top-right of the banner. Please direct posts to that thread, or try /r/OverwatchLFT or other websites. Thanks!""")
        self.comments = False

    def valid_post(self, post):
        return not any(phrase in post.title.lower() for phrase in ["need teammates for","LFG","LFT","LFM","recruit","start a team","[NA][PC]","[EU][PC]",
            "[NA][PS4]","[EU][PS4]","[PC][EU]","[PC][NA]","looking for team","looking for a team","looking for a competitive team",
            "looking for a competitive team","looking for people to play"])

class BugRule(Rule):
    def __init__(self):
        super().__init__(5, "Bugs, Meta & Balance Topics", "Blizzard keeps a list of known issues stickied at the top of their forums. Post bug reports [on their forums](http://us.battle.net/forums/en/overwatch/22813881/), where they have previously commented on discussions and are better able to take action.")
        self.comments = False

    def valid_post(self, post):
        return not any(phrase in post.title.lower() for phrase in ["issue with matchmaking", "bug", "wouldn't let me join", "server error"])

class Rules:

    __post_rules = [LFGRule(), SilentRule(), BehaviorRule(), OffTopicLowEffortRule()]
    __comment_rules = [SilentRule(), BehaviorRule()]

    @classmethod
    def validate_post(cls, post):

        for rule in cls.__post_rules:
            if rule.posts and not rule.valid_post(post):
                return (False, rule)

        return (True, None)

    @classmethod
    def validate_comment(cls, comment):

        for rule in cls.__comment_rules:
            if rule.comments and not rule.valid_comment(comment):
                return (False, rule)

        return (True, None)