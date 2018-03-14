import asyncio
import os
import logging
import json

import aiodns
import aiohttp

import framework
import api.call as call
import api.league as league
import limiter


logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.DEBUG, datefmt='%d/%m/%Y %H:%M:%S')
loop = asyncio.get_event_loop()


# Reads Riot API key from environment
try:
    api_key = os.environ["RIOT_API_KEY"]
except KeyError:
    logging.exception("Riot API key not set")

def process_league(fut):
    res = fut.result()
    if res[2] == 200:
        league = res[5]
        sid = [e["playerOrTeamId"] for e in league["entries"]]
        print("{r}: found {c} summoners".format(r=res[0].region, c=len(sid)))
        for s in sid:
            fname = "test/" + "sid-" + res[0].region + ".txt"
            with open(fname, "a") as f:
                f.write(s + "\n")
            res[0].queue_sid.put(s)

async def run():
    async with aiohttp.ClientSession(loop=loop) as session:
        fw = {}
        for r in call.REGIONS:
            fw[r] = framework.Framework(loop, session, r, (20, 1), (100, 120))
            fw[r].set_key(api_key)
        res = []
        for r in call.REGIONS:
            task = loop.create_task(league.get_challenger(fw[r], "RANKED_SOLO_5x5"))
            res.append(task)
            task.add_done_callback(process_league)
            task = loop.create_task(league.get_master(fw[r], "RANKED_SOLO_5x5"))
            res.append(task)
            task.add_done_callback(process_league)
            
        await asyncio.wait(res, loop=loop, return_when="ALL_COMPLETED")

loop.run_until_complete(run())
