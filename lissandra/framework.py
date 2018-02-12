import limiter
import asyncio

class Framework(object):
    def __init__(self, session, region, *limiters):
        self.loop = asyncio.get_event_loop()
        self.lim = limiter.MultiRateLimiter(*limiters)
        self.qp = None
        self.queue_sid = asyncio.Queue(loop=self.loop)
        self.session = session
        self.region = region
    
    def set_key(self, api_key):
        self.api_key = api_key

class QueuePipe(object):
    def __init__(self):
        pass