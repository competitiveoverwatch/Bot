import constants
import praw
from twitch.api import v3

reddit = praw.Reddit(client_id = constants.client_id,
                     client_secret = constants.client_secret,
                     password = constants.password,
                     user_agent = constants.user_agent,
                     username = constants.username)

subreddit = reddit.subreddit(constants.subreddit)