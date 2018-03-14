import asyncio
import os
import logging
import json

import aiodns
import aiohttp

import framework
import api.call as call
import api.league as league
import api.summoner as summoner
import api.match as match
import limiter


logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.DEBUG, datefmt='%d/%m/%Y %H:%M:%S')
loop = asyncio.get_event_loop()


# Reads Riot API key from environment
try:
    api_key = os.environ["RIOT_API_KEY"]
except KeyError:
    logging.exception("Riot API key not set")


aid = {}
aidstr = {}
for r in call.REGIONS:
    fname = "test/" + "aid-" + r + ".txt"
    with open(fname, "r") as f:
        aidstr[r] = f.readlines()
        aid[r] = [int(s) for s in aidstr[r]]

def process_matchlist(fut):
    res = fut.result()
    if res[2] == 200:
        ml = res[5]
        mid = [int(m["gameId"]) for m in ml["matches"]]
        print("{r}: downloaded {c} match ids".format(r=res[0].region, c=len(mid)))
        fname = "test/" + "mid-" + res[0].region + ".txt"
        with open(fname, "a") as f:
            for m in mid:
                f.write(str(m) + "\n")

async def run():
    async with aiohttp.ClientSession(loop=loop) as session:
        fw = {}
        for r in call.REGIONS:
            fw[r] = framework.Framework(loop, session, r, (20, 1), (100, 120))
            fw[r].set_key(api_key)
        res = []
        for r in call.REGIONS:
            for a in aid[r]:
                task = loop.create_task(match.get_matchlist(fw[r], a))
                res.append(task)
                task.add_done_callback(process_matchlist)
        await asyncio.wait(res, loop=loop, return_when="ALL_COMPLETED")

loop.run_until_complete(run()) 