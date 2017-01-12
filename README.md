# [/r/CompetitiveOverwatch](https://reddit.com/r/competitiveoverwatch)'s Sidebar Bot

##About
* Runs every 5 minutes
* Fetches sidebar template from wiki
* Replaces `{{MEGATHREADS}}` placeholder with the latest links to 3 weekly megathreads
* Replaces `{{EVENTS}}` placeholder with 6 upcoming Premier or Major events from [Liquipedia](http://wiki.teamliquid.net/overwatch/Portal:Tournaments)
    - Please remember to [follow their API guidelines](http://www.teamliquid.net/forum/hidden/491339-liquipedia-api-usage-guidelines)
* If Liquipedia lists a Twitch URL for an event, checks if the channel is live & adds a LIVE badge
* Updates actual sidebar text

##Technical

**Flow**
* `updateSidebar()`
    * `Reddit.getAuthToken()`
    * `Reddit.getSidebarTemplate()`
    * `updateMegathreads()`
    * `updateEvents()`
    * `Twitch.isChannelLive()`
    * `Reddit.postNewSidebar()`

**Information**
* Based on [chromakode/reddit-sidebar-updater](https://github.com/chromakode/reddit-sidebar-updater) with heavy modifications
* `UpdateSidebar.gs` uses a trigger to run every 5 minutes
* Libraries (contained within separate, named Google Apps Script 'projects'):
    - `Reddit.gs`
    - `Twitch.gs`

* `SUBREDDIT` (subreddit name, e.g. `CompetitiveOverwatch`), `CLIENT_ID`, `CLIENT_SECRET`, `USERNAME`, `PASSWORD` and `TWITCH_CLIENT_ID` are all passed to the `UpdateSidebar` script as 'Script properties' (File > Project properties > Script properties)

Cache times:
* Megathreads JSON: 1 hour
* Events JSON: 6 hours (maximum duration)
* Twitch channel ID: 6 hours (maximum duration)
* Twitch channel live status (boolean): 4 minutes (bot polls every 5 minutes)

* Google Apps Scripts don't seem to support a number of JavaScript functions, which can make life slightly more difficult
