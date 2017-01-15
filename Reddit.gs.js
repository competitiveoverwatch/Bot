// Maximum sidebar length, set by Reddit
var SIDEBAR_LENGTH_LIMIT = 5120

//Get OAuth2 token
function getAuthToken(username, password, clientId, clientSecret) {
    const CACHE_KEY = "access_token"
    const cache = CacheService.getScriptCache()
    
    const cached = cache.get(CACHE_KEY)
    if (cached != null) {
        return cached
    }
    
    var authData = UrlFetchApp.fetch("https://ssl.reddit.com/api/v1/access_token", {
        payload: {
            grant_type: "password",
            scope: "wikiread,wikiedit,read",
            username: username,
            password: password
        },
        method: "post",
        headers: {"Authorization": "Basic " + Utilities.base64Encode(clientId + ":" + clientSecret)}
    })
    authData = JSON.parse(authData)
    const authToken = authData["access_token"]
    cache.put(CACHE_KEY, authToken, 3600) //Cache for 60 minutes (3600 seconds)
    
    return authToken
}

function getWikiPageJSON(authToken, subreddit, pageName) {
    return UrlFetchApp.fetch("https://oauth.reddit.com/r/" + subreddit + "/wiki/" + pageName + ".json", {
        headers: {"Authorization": "bearer " + authToken}
    })
}

//Get sidebar template from subreddit"s wiki
function getSidebarTemplate(authToken, subreddit) {
    var templateData = getWikiPageJSON(authToken, subreddit, "sidebar_template")
    templateData = JSON.parse(templateData)
    
    var template = templateData["data"]["content_md"]
    template = template
        .replace(/&amp;/g, "&")
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&quot;/g, '"')
        
    return template
}

function postNewSidebar(authToken, subreddit, sidebar) {
    const result = UrlFetchApp.fetch("https://oauth.reddit.com/r/" + subreddit + "/api/wiki/edit", {
        payload: {
            content: sidebar,
            page: "config/sidebar",
            reason: "Automated Google Apps Script update"
        },
        method: "post",
        headers: {"Authorization": "bearer " + authToken},
        muteHttpExceptions: true
    })
}