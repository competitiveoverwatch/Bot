from config import data as config
import praw

blacklist = ["MRW ","MFW ","[rant]","retard","cunt","kys","kill yourself","why the hell","why are you able to","sick and tired",
"fuck","console fags","you retarded","you're a fucking","nigger","suck dick","autism","fag","fuck that country"]

class Rule:
    def __init__(self, number, rules_json):
        self.number = number

        if self.number > 0 and rules_json is not None:
            self.__parse_definition_json(rules_json)

        self.posts = True
        self.comments = True
        
    def __parse_definition_json(self, json):
        if json is not None:
            this_rule = json[self.number - 1]

            self.name = "Rule " + this_rule["short_name"]
            self.description = this_rule["description"]

    def formatted(self):
        if self.description is not None:

            formatted_text = ""

            if self.name is not None:
                formatted_text += f"[{self.name}](https://reddit.com/r/{config.subredditName}/about/rules)\n\n"

            formatted_text += self.description

            return formatted_text

        else:
            return None

    # These methods to be implemented by subclasses
    def valid_post(self, post):
        pass

    def valid_comment(self, comment):
        pass

class SilentRule(Rule):

    def __init__(self):
        super().__init__(-1, None)

    def valid_post(self, post):
        return (post.author.comment_karma > -90 and not "elo hell" in post.title.lower())

    def valid_comment(self, comment):
        return (comment.author.comment_karma > -90)

class BehaviorRule(Rule):
    def __init__(self, rules_json):
        super().__init__(1, rules_json)

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
    def __init__(self, rules_json):
        super().__init__(2, rules_json)

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
    def __init__(self, megathread_url):
        super().__init__(-1, None)

        self.name = ""
        self.description = config.moderation.lfgRemovalDescriptionFormat.format(lfg_megathread_url = megathread_url)

        self.comments = False

    def valid_post(self, post):
        return not any(phrase in post.title.lower() for phrase in ["need teammates for","LFG","LFT","LFM","recruit","start a team",
            "[NA][PC]","[EU][PC]","[NA][PS4]","[EU][PS4]","[PC][EU]","[PC][NA]","looking for team","looking for a team",
            "looking for a competitive team","looking for a competetive team","looking for people to play"])

class BugRule(Rule):
    def __init__(self, rules_json):
        super().__init__(5, rules_json)
        self.comments = False

    def valid_post(self, post):
        return not any(phrase in post.title.lower() for phrase in ["issue with matchmaking", "bug", "wouldn't let me join", "server error"])

class Rules:    

    def __init__(self, subreddit, megathreads):
        self.subreddit = subreddit
        self.megathreads = megathreads

        rules_json = self.subreddit.rules()["rules"]

        # Get the URL for the latest LFG megathread for the LFG removal rule
        megathreads_list = self.megathreads.get_latest()

        lfg_megathread_url = None
        for thread in megathreads_list:

            if "LFG" in thread["title"]:
                lfg_megathread_url = thread["url"]
                break

        self.__post_rules = [LFGRule(lfg_megathread_url), SilentRule(), BehaviorRule(rules_json), OffTopicLowEffortRule(rules_json)]
        self.__comment_rules = [SilentRule(), BehaviorRule(rules_json)]

    def validate_post(self, post):

        for rule in self.__post_rules:
            if rule.posts and not rule.valid_post(post):
                return (False, rule)

        return (True, None)

    def validate_comment(self, comment):

        for rule in self.__comment_rules:
            if rule.comments and not rule.valid_comment(comment):
                return (False, rule)

        return (True, None)
