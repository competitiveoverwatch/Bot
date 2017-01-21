# [/r/CompetitiveOverwatch](https://reddit.com/r/competitiveoverwatch)'s Sidebar Bot

##About
* Updates sidebar every 5 minutes
    - Fetches sidebar template from wiki
    - Replaces `{{MEGATHREADS}}` placeholder with the latest links to 3 weekly megathreads
    - Replaces `{{EVENTS}}` placeholder with 6 upcoming Premier or Major events from [Liquipedia](http://wiki.teamliquid.net/overwatch/Portal:Tournaments)
        - Please remember to [follow their API guidelines](http://www.teamliquid.net/forum/hidden/491339-liquipedia-api-usage-guidelines)
    - If Liquipedia lists a Twitch URL for an event, checks if the channel is live & adds a LIVE badge
    - Updates actual sidebar text