import asyncio
import logging
import enum

import api

class RequestMode(enum.Enum):
    match = 1
    matchlist = 2
    summoner = 3


class Request(object):

    MATCH_BATCH = 10
    MATCHLIST_BATCH = 20
    MATCHLIST_MAX_ELAPSED_DAYS = 0

    def __init__(self, fw):
        self.match_counter = 0
        self.matchlist_counter = 0
        self.mode = RequestMode.match
        self.queue_matchlist = asyncio.Queue()
        self.queue_match = asyncio.PriorityQueue()
        self.flag_exit = asyncio.Event()
        self.cur_request = None
        self.count = 0
        self.fw = fw

    async def run(self):
        while not self.flag_exit.is_set():
            if self.mode == RequestMode.match and not self.queue_match.empty():
                mid = await self.queue_match.get()
                mid = mid[1]
                res = None
                try:
                    async with self.fw.lim:
                        res = await api.get_match(self.fw, mid)
                except:
                    raise
                finally:
                    if res is not None:
                        if res[2] == 200:
                            print(res[5])
                        else:
                            print("Error while getting match {mid}: {e}".format(mid=mid, e=res[2]))
                    self.count += 1
                    if self.count >= Request.MATCH_BATCH:
                        self.count = 0
                        self.mode = RequestMode.matchlist
            
            else:
                self.mode = RequestMode.match
                    
