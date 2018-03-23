import asyncio
import logging
from pathlib import Path

from limiter import MultiRateLimiter
from db import DBMatch
from db import DBMatchlist

class APIClient(object):
    def __init__(self, region, session, key, data_path):
        self.region = region
        self.limiter = MultiRateLimiter((20, 1), (100, 120))
        self.session = session
        self.key = key
        self.loop = asyncio.get_event_loop()
        self.queue_sid = asyncio.Queue(loop=self.loop)
        self.queue_mid = asyncio.Queue(loop=self.loop)
        self.queue_aid = asyncio.Queue(loop=self.loop)
        self.exiting = False
        self.shutdown = asyncio.Event()

        # Creates folder structure
        self.dir_data = data_path
        self.dir_region = Path(
            self.dir_data, self.region.lower())
        self.dir_db = Path(self.dir_region, 'db')
        self.dir_match = Path(self.dir_region, 'match')
        try:
            self.dir_data.mkdir(exist_ok=True)
            self.dir_region.mkdir(exist_ok=True)
            self.dir_db.mkdir(exist_ok=True)
            self.dir_match.mkdir(exist_ok=True)
        except OSError:
            logging.error("Failed to create folder structure")
            sys.exit(3)

        # Initialize databases
        self.fname_db_match = Path(
            self.dir_db, "db-disc-match-" +
            self.region.lower() + ".sqlite")
        self.fname_db_matchlist = Path(
            self.dir_db, "db-disc-matchlist-" +
            self.region.lower() + ".sqlite")
        self.fname_db_summoner = Path(
            self.dir_db, "db-disc-summoner-" +
            self.region.lower() + ".sqlite")

        self.db_match = DBMatch(self.fname_db_match)
        self.db_matchlist = DBMatchlist(self.fname_db_matchlist)

        # Initialize tasks
        self.tasks = {}
        self.tasks["mgr"] = None # Manager
        self.tasks["req"] = None # Request
        self.tasks["dsp"] = None # Dispatch
        self.tasks["fls"] = None # Flush
        self.tasks["rpt"] = None # Status report

        logging.debug("Initialized client for region {r}".format(r=region))
