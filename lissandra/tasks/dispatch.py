import asyncio
import logging

import lissandra


class Dispatch(object):
    def __init__(self):
        pass

    async def run(self):
        logging.debug("Dispatcher started")
        try:
            count = await lissandra.db_match.count("MatchDiscovered")
            print("Matches discovered: {md}".format(md=count))
        except:
            logging.error("Failed to count")
        await asyncio.sleep(5)
