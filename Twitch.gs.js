function getIdForChannel(clientId, channelName) {
    const CACHE_KEY = channelName+"_id"
    const cache = CacheService.getScriptCache()
    
    const cachedId = cache.get(CACHE_KEY)
    if (cachedId != null) {
        Logger.log("Returning cached channel ID")
        return cachedId
    }
    
    var responseData = UrlFetchApp.fetch("https://api.twitch.tv/kraken/search/channels?query="+channelName+"&limit=1", {
        headers: {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": clientId
        }
    })
    responseData = JSON.parse(responseData)
    
    const channelId = responseData.channels[0]._id
    
    //Cache for 6 hours (21,600 seconds)
    //Which is the longest supported cache time
    //https://developers.google.com/apps-script/reference/cache/cache#putkey-value-expirationinseconds
    cache.put(CACHE_KEY, channelId, 21600)
    
    return channelId
}

function isChannelLive(clientId, channelName) {
    const channelId = Number(getIdForChannel(clientId, channelName)).toString()
    
    const CACHE_KEY = channelName+"_live"
    const CACHE_TIME = 60*4 //4 minutes
    const cache = CacheService.getScriptCache()
    
    const cachedBoolean = cache.get(CACHE_KEY)
    if (cachedBoolean != null) {
        Logger.log("Returning cached Live boolean")
        return cachedBoolean
    }
    
    var responseData = UrlFetchApp.fetch("https://api.twitch.tv/kraken/streams/"+channelId, {
        headers: {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": clientId
        }
    })
    responseData = JSON.parse(responseData)
    
    const channelLive = (responseData.stream != null)
    cache.put(CACHE_KEY, channelLive, CACHE_TIME)
    
    return channelLive
}