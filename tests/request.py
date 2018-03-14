import asyncio
import os
import logging
import json
import concurrent.futures

import aiodns
import aiohttp

import framework
import api.call as call
import api.league as league
import api.summoner as summoner
import api.match as match
import tasks.request
import limiter


logging.basicConfig(format='%(asctime)s: %(message)s',
    level=logging.DEBUG,
    datefmt='%d/%m/%Y %H:%M:%S')
loop = asyncio.get_event_loop()

region = "BR"

# Reads Riot API key from environment
try:
    api_key = os.environ["RIOT_API_KEY"]
except KeyError:
    logging.exception("Riot API key not set")

# Get match ids and fill queue
fname = "test/" + "mid-" + region + ".txt"
with open(fname, "r") as f:
    match_ids = [int(s) for s in f.readlines()]

queue_match = asyncio.PriorityQueue()
for m in match_ids:
    queue_match.put_nowait((-m, m))

async def run():
    async with aiohttp.ClientSession() as session:
        fw = framework.Framework(session, region, (20, 1), (100, 120))
        fw.set_key(api_key)
        req = tasks.request.Request(fw)
        req.queue_match = queue_match
        await req.run()

loop.run_until_complete(run()) 