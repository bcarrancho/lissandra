import asyncio
import logging

from tasks.dispatch import Dispatch
#from tasks.request import Request


class Manager(object):
    def __init__(self, client):
        self.client = client
    

    def start_dispatch(self):
        self.client.dispatch = Dispatch(self.client)
        self.client.tasks["dsp"] = self.client.loop.create_task(
            self.client.dispatch.run())


    async def run(self):
        logging.debug("{r}: Manager started".format(r=self.client.region))
        self.start_dispatch()
        #self.start_request()
        #self.start_flush()
        #self.start_report()
        while not self.client.exiting:
            await asyncio.sleep(5)
        await self.client.tasks["dsp"]
        
        logging.debug("{r}: Manager terminated".format(r=self.client.region))
        self.client.shutdown.set()
