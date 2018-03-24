import asyncio
import logging


class Dispatch(object):
    def __init__(self, client):
        self.client = client

    async def run(self):
        logging.debug("{r}: Dispatcher started".format(r=self.client.region))
        try:
            count = await self.client.db_match.count("MatchDiscovered")
            print("{r}: Matches discovered: {md}".format(
                md=count, r=self.client.region))
        except:
            logging.error("{r}: Failed to count".format(r=self.client.region))
        await asyncio.sleep(5)

        # Main loop
        while not self.client.exiting:
            await asyncio.sleep(3)

        logging.debug("{r}: Dispatch terminated".format(r=self.client.region))
