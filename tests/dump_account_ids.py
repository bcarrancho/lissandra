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
import limiter


logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.DEBUG, datefmt='%d/%m/%Y %H:%M:%S')
loop = asyncio.get_event_loop()


# Reads Riot API key from environment
try:
    api_key = os.environ["RIOT_API_KEY"]
except KeyError:
    logging.exception("Riot API key not set")


sid = {}
sidstr = {}
for r in call.REGIONS:
    fname = "test/" + "sid-" + r + ".txt"
    with open(fname, "r") as f:
        sidstr[r] = f.readlines()
        sid[r] = [int(s) for s in sidstr[r]]

def process_summoner(fut):
    res = fut.result()
    if res[2] == 200:
        summoner = res[5]
        aid = summoner["accountId"]
        #print("{r}: downloaded summoner {s}".format(r=res[0].region, s=aid))
        fname = "test/" + "aid-" + res[0].region + ".txt"
        with open(fname, "a") as f:
            f.write(str(aid) + "\n")

async def run():
    async with aiohttp.ClientSession(loop=loop) as session:
        fw = {}
        for r in call.REGIONS:
            fw[r] = framework.Framework(loop, session, r, (20, 1), (100, 120))
            fw[r].set_key(api_key)
        res = []
        for r in call.REGIONS:
            for s in sid[r]:
                task = loop.create_task(summoner.get_summoner(fw[r], s))
                res.append(task)
                task.add_done_callback(process_summoner)
        await asyncio.wait(res, loop=loop, return_when="ALL_COMPLETED")

loop.run_until_complete(run())