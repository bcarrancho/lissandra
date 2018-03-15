import asyncio
import logging

import lissandra
from tasks.dispatch import Dispatch
from tasks.request import Request
#from tasks.report import Report
#from tasks.flush import Flush


class Manager(object):
    def __init__(self):
        pass
    
    def start_dispatch(self):
        lissandra.dispatch = Dispatch()
        lissandra.tasks["dsp"] = lissandra.loop.create_task(
            lissandra.dispatch.run())


    def start_request(self):
        lissandra.request = Request()
        lissandra.tasks["req"] = lissandra.loop.create_task(
            lissandra.request.run())


    def start_flush(self):
        lissandra.flush = Flush()
        lissandra.tasks["fls"] = lissandra.loop.create_task(
            lissandra.flush.run())


    def start_report(self):
        lissandra.report = Report()
        lissandra.tasks["rpt"] = lissandra.loop.create_task(
            lissandra.report.run())


    async def run(self):
        logging.debug("Manager started")
        self.start_dispatch()
        #self.start_request()
        #self.start_flush()
        #self.start_report()
        while not lissandra.exiting:
            await asyncio.sleep(5)
        logging.debug("Manager terminated")
