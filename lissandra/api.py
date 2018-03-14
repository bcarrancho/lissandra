import logging

ENDPOINTS = {"BR": "br1",
        "EUNE": "eun1",
        "EUW": "euw1",
        "JP": "jp1",
        "KR": "kr",
        "LAN": "la1",
        "LAS": "la2",
        "NA": "na1",
        "OCE": "oc1",
        "TR": "tr1",
        "RU": "ru"}
REGIONS = ENDPOINTS.keys()

async def api_call(fw, url):
    header = {"X-Riot-Token": fw.api_key}
    async with fw.session.get(url, headers=header) as resp:
        json = None
        # Parse response
        if resp.status == 200:
            json = await resp.json()
            retry_after = None
        elif resp.status in [400, 403, 415]:
            print(resp.header)
            raise ValueError
        elif resp.status == 404:
            logging.warning("404: {url}".format(url=url))
            retry_after = None
        elif resp.status == 429:
            retry_after = int(resp.headers.get("Retry-After", "1")) + 1
            logging.warning("429: Retry-After {ra} s".format(ra=retry_after - 1))
        elif resp.status in [500, 503, 504]:
            retry_after = 30
        
        if retry_after is not None:
            fw.lim.update_resetter(retry_after)
            fw.loop.create_task(fw.lim.call(api_call, fw, url))
        
        return (fw, resp.url, resp.status, resp.headers, retry_after, json)


async def get_challenger(fw, queue):
    url = "https://" +
        ENDPOINTS[fw.region] +
        ".api.riotgames.com/lol/league/v3/challengerleagues/by-queue/" +
        queue
    return await fw.lim.call(api_call, fw, url)

async def get_master(fw, queue):
    url = "https://" +
        ENDPOINTS[fw.region] +
        ".api.riotgames.com/lol/league/v3/masterleagues/by-queue/" +
        queue
    return await fw.lim.call(api_call, fw, url)

async def get_match(fw, mid):
    url = "https://" +
        ENDPOINTS[fw.region] +
        ".api.riotgames.com/lol/match/v3/matches/"
        + str(mid)
    return await fw.lim.call(api_call, fw, url)

async def get_matchlist(fw, aid):
    url = "https://" +
        ENDPOINTS[fw.region] +
        ".api.riotgames.com/lol/match/v3/matchlists/by-account/" +
        str(aid)
    return await fw.lim.call(api_call, fw, url)

async def get_summoner(fw, sid):
    url = "https://" +
        ENDPOINTS[fw.region] +
        ".api.riotgames.com/lol/summoner/v3/summoners/" +
        str(sid)
    return await fw.lim.call(api_call, fw, url)