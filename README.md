# [/r/CompetitiveOverwatch](https://reddit.com/r/competitiveoverwatch)'s Sidebar Bot

##About
* Runs hourly
* Fetches sidebar template from wiki
* Replaces `{{MEGATHREADS}}` placeholder with the latest links to 3 weekly megathreads
* Replaces `{{EVENTS}}` placeholder with 6 upcoming Premier or Major events from [Liquipedia](http://wiki.teamliquid.net/overwatch/Portal:Tournaments)
    - Please remember to [follow their API guidelines](http://www.teamliquid.net/forum/hidden/491339-liquipedia-api-usage-guidelines)
* Updates actual sidebar text

##Technical

**Outline**
* `updateSidebar()`
    * `Reddit.getAuthToken()`
    * `Reddit.getSidebarTemplate()`
    * `updateMegathreads()`
    * `updateEvents()`
    * `Reddit.postNewSidebar()`

**Information**
* Based on [chromakode/reddit-sidebar-updater](https://github.com/chromakode/reddit-sidebar-updater) with heavy modifications
* `UpdateSidebar.gs` uses an hourly trigger
* `Reddit.gs` is contained within a separate `Reddit` 'project', and used as a `Library` for the main `Sidebar Bot` project

* `SUBREDDIT` (subreddit name, e.g. `CompetitiveOverwatch`), `CLIENT_ID`, `CLIENT_SECRET`, `USERNAME`, `PASSWORD` are all passed to the `UpdateSidebar` script as 'Script properties' (File > Project properties > Script properties)

* Megathreads JSON is cached for 1 hour
* Events JSON is cached for 3 hours

* Google Apps Scripts don't seem to support a number of JavaScript functions, which can make life slightly more difficult
