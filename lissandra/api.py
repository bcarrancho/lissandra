import logging

import lissandra
from common import REGIONS
from common import ENDPOINTS


async def api_call(fw, url):
    header = {"X-Riot-Token": lissandra.api_key}
    async with lissandra.session.get(url, headers=header) as resp:
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
            lissandra.limiter.update_resetter(retry_after)
            lissandra.loop.create_task(lissandra.limiter.call(api_call, fw, url))
        
        return (fw, resp.url, resp.status, resp.headers, retry_after, json)


async def get_challenger(fw, queue):
    url = "https://" + ENDPOINTS[lissandra.region] + ".api.riotgames.com/lol/league/v3/challengerleagues/by-queue/" + queue
    return await lissandra.limiter.call(api_call, fw, url)

async def get_master(fw, queue):
    url = "https://" + ENDPOINTS[lissandra.region] + ".api.riotgames.com/lol/league/v3/masterleagues/by-queue/" + queue
    return await lissandra.limiter.call(api_call, fw, url)

async def get_match(fw, mid):
    url = "https://" + ENDPOINTS[lissandra.region] + ".api.riotgames.com/lol/match/v3/matches/" + str(mid)
    return await lissandra.limiter.call(api_call, fw, url)

async def get_matchlist(fw, aid):
    url = "https://" + ENDPOINTS[lissandra.region] + ".api.riotgames.com/lol/match/v3/matchlists/by-account/" + str(aid)
    return await lissandra.limiter.call(api_call, fw, url)

async def get_summoner(fw, sid):
    url = "https://" + ENDPOINTS[lissandra.region] + ".api.riotgames.com/lol/summoner/v3/summoners/" + str(sid)
    return await lissandra.limiter.call(api_call, fw, url)