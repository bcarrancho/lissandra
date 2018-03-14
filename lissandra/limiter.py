import asyncio
import time

class SingleRateLimiter(object):

    def __init__(self, calls_per_epoch, seconds_per_epoch):
        self.loop = asyncio.get_event_loop()
        self.calls_per_epoch = calls_per_epoch
        self.seconds_per_epoch = seconds_per_epoch
        self.semaphore = asyncio.BoundedSemaphore(calls_per_epoch)
        self.lock = asyncio.Lock()
        self.resetter = None
        self.reset_time = None
    
    def reset(self):
        self.resetter = None
        self.reset_time = None
        try:
            for i in range(self.calls_per_epoch):
                self.semaphore.release()
        except ValueError:
            pass

    async def __aenter__(self):
        await self.semaphore.acquire()
        await self.lock.acquire()
        self.set_resetter()

    async def __aexit__(self, exc_type, exc, tb):
        self.lock.release()

    def set_resetter(self, update=False, delay=0):
        if delay == 0:
            delay = self.seconds_per_epoch
        
        if not update:
            if self.resetter is None:
                self.resetter = self.loop.call_later(delay, self.reset)
                self.reset_time = time.time() + delay
        else:
            if self.reset_time is not None:
                if self.reset_time < time.time() + delay:
                    if self.resetter is not None:
                        self.resetter.cancel()
                    self.resetter = self.loop.call_later(delay, self.reset)
                    self.reset_time = time.time() + delay
            else:
                self.resetter = self.loop.call_later(delay, self.reset)
                self.reset_time = time.time() + delay

        
    async def call(self, method, *args):
        async with self:
            return await method(*args)


class MultiRateLimiter(object):

    def __init__(self, *limiters):
        self.loop = asyncio.get_event_loop()
        
        # Returns a sorted list of limiters
        dict_limiters = {}
        for limiter in limiters:
            dict_limiters[int(limiter[1])] = SingleRateLimiter(limiter[0], limiter[1])
        sorted_keylist = sorted(dict_limiters.keys(), reverse=True)
        self.limiters = []
        for key in sorted_keylist:
            self.limiters.append(dict_limiters[key])
    
    async def __aenter__(self):
        for limiter in self.limiters:
            await limiter.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        for limiter in self.limiters:
            await limiter.__aexit__(exc_type, exc, tb)

    def set_resetter(self):
        for limiter in self.limiters:
            limiter.set_resetter()

    def update_resetter(self, delay):
        for limiter in self.limiters:
            limiter.set_resetter(update=True, delay=delay)

    async def call(self, method, *args):
        async with self:
            return await method(*args)
