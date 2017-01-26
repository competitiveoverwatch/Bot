class Rule():
	def __init__(self, number, name, description):
		self.number = number
		self.posts = True
		self.comments = True
		self.name = name
		self.description = description

class Rule1(Rule):
	def __init__(self):
		super().__init__(1, "No Poor or Abusive Behavior", """Posts and comments that are toxic or break Reddiquette will be removed. This includes, but is not limited to:
 
* Personal attacks and hateful language
* Witch-hunts and vote brigading
* Posting other users' personal information without consent (doxing)
* Offering, requesting, or linking to cheats, rank manipulation, or game-breaking exploits
 
If you see doxing, [message the mod team](https://www.reddit.com/message/compose?to=%2Fr%2FCompetitiveoverwatch) immediately.""")

class Rule2(Rule):
	def __init__(self):
		super().__init__(2, "No Off-Topic or Low-effort Content", """Off-topic and low-effort content can flood the subreddit and drown out meaningful discussion. As such, it is prohibited. This includes, but is not limited to:

* Posts not related to competitive mode / Overwatch esports
* Non-constructive complaints / rants 
* Screenshots / Highlight Videos / Gifs (see Rule 8)
* General gameplay videos
* Re-posted / repetitive content (please search before you post)
 
Post smaller questions in the Weekly Discussion Megathread (right side of the header).""" )
		self.comments = False

	@classmethod
	def valid_submission(submission):
		pass

class Rules():

	__rules = [Rule1(), Rule2()]

	@classmethod
	def validate_submission(submission):
		title = submission.title.lower()
		title_length_chars = len(title)
		title_length_words = len(title.split())

		for rule in __rules:
			if not rule.valid_submission(submission):
				return False

		return True

