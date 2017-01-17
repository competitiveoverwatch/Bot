// spiffy sidebar updater
// https://github.com/chromakode/reddit-sidebar-updater
//
// Copyright (c) 2014 Max Goodman.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 1. Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
// 3. The name of the author or contributors may not be used to endorse or
//    promote products derived from this software without specific prior
//    written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
// OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
// OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
// SUCH DAMAGE.

//Based on the above with heavy modifications

var scriptProperties = PropertiesService.getScriptProperties()

var SUBREDDIT = scriptProperties.getProperty("SUBREDDIT")

// Register "script" type Reddit OAuth2 app at reddit.com/prefs/apps for these:
var CLIENT_ID = scriptProperties.getProperty("CLIENT_ID") // OAuth2 client ID
var CLIENT_SECRET = scriptProperties.getProperty("CLIENT_SECRET")  // OAuth2 client secret

// Create a user solely for this script and mod them with wiki permissions.
var USERNAME = scriptProperties.getProperty("USERNAME")
var PASSWORD = scriptProperties.getProperty("PASSWORD")

var USER_AGENT = "r/" + SUBREDDIT + " sidebar updater. (Contact us via r/" + SUBREDDIT + " modmail)"

//Twitch
var TWITCH_CLIENT_ID = scriptProperties.getProperty("TWITCH_CLIENT_ID")

function updateSidebar() {
    const authToken = Reddit.getAuthToken(USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET)
    
    var sidebar = Reddit.getSidebarTemplate(authToken, SUBREDDIT)
    sidebar = updateMegathreads(authToken, sidebar)
    sidebar = updateEvents(authToken, sidebar)
    
    Reddit.updateSidebar(authToken, SUBREDDIT, sidebar)
}

//String formatting solution from http://stackoverflow.com/a/21844011/447697
//Seeing as ES6/ES2015 string templating isn't available
String.prototype.format = function() {
    var s = this, i = arguments.length

    while (i--) {
        s = s.replace(new RegExp("\\{" + i + "\\}", "gm"), arguments[i])
    }
    return s
}

function encodeURLParams(params) {
    return Object.keys(params).map(function(key) {
        return encodeURIComponent(key) + "=" + encodeURIComponent(params[key])
    }).join("&")
}

function getMegathreadsJSON(searchUrl) {
    var CACHE_KEY = encodeURI("megathreads_json")
    const cache = CacheService.getScriptCache()
    
    var cached = cache.get(CACHE_KEY)
    if (cached != null) {
        Logger.log("Returning cached megathreads")
        return cached
    }
    
    Logger.log("No cached megathreads")
    
    var responseData = UrlFetchApp.fetch(searchUrl, {
        headers: {
            "User-Agent": USER_AGENT
        }
    })
    cache.put(CACHE_KEY, responseData, 3600) //Cache for 1 hour (3600 seconds)
    return responseData
}

function updateMegathreads(authToken, sidebar) {
    var MEGATHREAD_TITLES = ["LFG: Find Players & Teams", "Advice: Questions & VOD Reviews", "Discussion Megathread"]
    var MEGATHREAD_KEYWORDS = ["lfg", "advice", "discussion"]
    
    const searchParams = {
        subreddit: "competitiveoverwatch",
        self: "yes",
        flair: "megathread",
        author: "automoderator"
    }
    
    const searchURLSuffix = "&" + encodeURLParams({
        restrict_sr:"on",
        sort:"new",
        t:"month"
    })
    
    const searchURL = "https://api.reddit.com/r/"+SUBREDDIT+"/search.json?q=" + Object.keys(searchParams).map(function(k) {
        return encodeURIComponent(k + ":" + searchParams[k])
    }).join("+") + searchURLSuffix
    
    var megathreadsJSON = getMegathreadsJSON(searchURL)
    var megathreads = JSON.parse(megathreadsJSON).data.children
    
    //Format megathreads
    var megathreadsStr = ""
    
    for (var key in megathreads) {
        if (MEGATHREAD_KEYWORDS.length == 0) {
            break
        }
    
        if (megathreads.hasOwnProperty(key)) {
            var megathread = megathreads[key].data
            var title = megathread.title.toLowerCase()
        
            var index = -1
            
            for (var i = 0; i < MEGATHREAD_KEYWORDS.length; i++) {
                if (title.indexOf(MEGATHREAD_KEYWORDS[i]) !== -1) {
                    index = i
                    title = MEGATHREAD_TITLES[i]
                    break
                }
            }
            
            if (index > -1) {
                //Removed used title/keyword + shorten search
                MEGATHREAD_TITLES.splice(index,1)
                MEGATHREAD_KEYWORDS.splice(index,1)
            
                var link = megathread.url
                megathreadsStr += "> ["+title+"]("+link+")\n"
            }
        }
    }
    
    return sidebar.replace("{{MEGATHREADS}}", megathreadsStr)
}

var BYPASS_EVENT_CACHE = false

function getEventsJSON() {
    const CACHE_KEY = "events_json"
    
    const EVENTS_URL_BASE = "http://wiki.teamliquid.net/overwatch/api.php?"
    
    const QUERY = [
        "[[Category:Tournaments]]",
        "[[Is tier::Premier||Major]]",
        "[[Has_end_date::>]]",
        "?Has_name",
        "?Has_tournament_twitch",
        "?Has_start_date",
        "?Has_end_date",
        "?Has_prize_pool",
        "offset=0",
        "limit=6",
        "sort=Has_start_date",
        "order=asc"
    ]
    
    const EVENTS_URL = EVENTS_URL_BASE + encodeURLParams({
        action: "ask",
        query: QUERY.join("|"),
        format: "json"
    })
    
    const cache = CacheService.getScriptCache()
    
    if (!BYPASS_EVENT_CACHE) {
        const cached = cache.get(CACHE_KEY)
        
        if (cached != null) {
            Logger.log("Returning cached events")
            return cached
        }
        
        Logger.log("No cached events")
    }
    
    var responseData = UrlFetchApp.fetch(EVENTS_URL, {
        headers: {
            "User-Agent": USER_AGENT
        }
    })
    cache.put(CACHE_KEY, responseData, 21600) //Cache for 6 hours (21600 seconds)
    return responseData
}

//For some reason, Google Apps Scripts don't support .toLocaleString
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function updateEvents(authToken, sidebar) {

    var events = JSON.parse(getEventsJSON()).query.results
    
    const eventFormat = "####[{0}{1}]({2}){3}\n\n{4}\n\n"
    const prizepoolFormat = "\n\n${0} Prize Pool"
    const dateFormat = "**{0} – {1}**"
    
    var eventsStr = ""
    var sidebarLength = sidebar.length - "{{EVENTS}}".length
    
    for (var eventKey in events) {
        var event = events[eventKey]
        var eventName = event.printouts["Has name"]
        
        var twitchUrl = event.printouts["Has tournament twitch"]
        var twitchChannelLive = false
        var liveBadge
        if (twitchUrl == "") {
            twitchUrl = event.fullurl
            
        } else {
            var urlComponents = twitchUrl.toString().split("/")
            var twitchChannelName = urlComponents[urlComponents.length-1]
            twitchChannelLive = Twitch.isChannelLive(TWITCH_CLIENT_ID, twitchChannelName)
        }
        var liveBadge = (twitchChannelLive == true)? "**LIVE:** " : ""
        
        var startTimestamp = event.printouts["Has start date"] * 1000
        var endTimestamp = event.printouts["Has end date"] * 1000
        var start = new Date(startTimestamp)
        var end = new Date(endTimestamp)
        
        var now = new Date()
        
        var eventDates
        //If start == end, event may have been rescheduled/something else happened
        //e.g. this happened with Masters Gaming Arena 2016
        if (startTimestamp == endTimestamp) {
            eventDates = "Dates TBA"
        
        } else {
            var formattedStart
            if (start <= now) {
                formattedStart = "Ongoing"
            } else {
                formattedStart = Utilities.formatDate(start, "UTC", "MMMM d")
            }
            
            var formattedEnd
            //Check `start >= now` to avoid "Ongoing – 31"/similar nonsense
            if (start.getMonth() == end.getMonth() && start > now) {
                formattedEnd = Utilities.formatDate(end, "UTC", "d")
            } else {
                formattedEnd = Utilities.formatDate(end, "UTC", "MMMM d")
            }
            
            eventDates = dateFormat.format(formattedStart, formattedEnd)
        }
        
        var prizepool = event.printouts["Has prize pool"]
        var currency = event.printouts["Has localcurrency"]
        var formattedPrizepool = ""
        if (prizepool > 0) {
            //Round prizepool to nearest 10, add commas
            prizepool = Math.round(Number(prizepool) / 10) * 10
            formattedPrizepool = prizepoolFormat.format(numberWithCommas(prizepool))
        }
        
        var newEvent = eventFormat.format(liveBadge,eventName,twitchUrl,formattedPrizepool,eventDates)

        if (sidebarLength + newEvent.length > Reddit.SIDEBAR_LENGTH_LIMIT) {
            break
        } else {
            eventsStr += newEvent
            sidebarLength += newEvent.length
        }
    }
    
    return sidebar.replace("{{EVENTS}}", eventsStr)
}