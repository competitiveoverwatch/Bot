from config import data as config

import arrow
import requests
import requests.exceptions

class Team:

    def __init__(self, team_json):
        # Name and country can be null if the team is still TBD for a match
        self.name = None
        self.country = None

        self.__parse_json(team_json)

    def __parse_json(self, team_json):
        self.name = team_json["name"]

        # 2-character ISO country code
        self.country_code = team_json["country"]

class Match:

    def __init__(self, match_json):
        self.__parse_json(match_json)

    def __parse_json(self, match_json):
        self.start = arrow.get(match_json["timestamp"])
        self.event = match_json["event_name"]
        self.over_gg_link = match_json["match_link"]

        self.teams = []

        for team in match_json["teams"]:
            self.teams.append(Team(team))

    def is_live(self):
        return self.start > arrow.utcnow()

class Matches:

    def __init__(self, logger):
        self.logger = logger

    def __get_matches_json(self):
        try:
            data = requests.get(config.creds.overGGMatchesUpcoming, headers = {
                "User-Agent": config.userAgentFormat.format(subreddit = config.subredditName)
            })
            data.raise_for_status()
            data = data.json()
            return data

        except Exception as e:
            self.logger.exception(e)
            return None

    def get_formatted(self, sidebar_length):
        data = self.__get_matches_json()

        if data is None:
            return data

        else:
            matches_data = data["matches"]

            matches = []

            for match in matches_data:
                matches.append(Match(match))

            return ""