import argparse
import asyncio
import logging
from pathlib import Path
import os
import sys

import lissandra
from limiter import MultiRateLimiter
from common import REGIONS

def main(parameters):
    lissandra.key = parameters["key"]
    lissandra.region = parameters["region"]
    lissandra.loop = asyncio.get_event_loop()

    # Instantiate a limiter with development limits
    lissandra.limiter = MultiRateLimiter((20, 1), (100, 120))
    lissandra.queue_sid = asyncio.Queue(loop=lissandra.loop)
    lissandra.queue_mid = asyncio.Queue(loop=lissandra.loop)
    lissandra.queue_aid = asyncio.Queue(loop=lissandra.loop)

    # Initialize data directory structure
    lissandra.dir_data = Path('.', 'data')
    lissandra.dir_region = Path(
        lissandra.dir_data, lissandra.region.lower())
    lissandra.dir_db = Path(lissandra.dir_region, 'db')
    lissandra.dir_match = Path(lissandra.dir_region, 'match')
    try:
        lissandra.dir_data.mkdir(exist_ok=True)
        lissandra.dir_region.mkdir(exist_ok=True)
        lissandra.dir_db.mkdir(exist_ok=True)
        lissandra.dir_match.mkdir(exist_ok=True)
    except OSError:
        logging.error("Failed to create folder structure")
        sys.exit(3)

    # Initialize databases



if __name__ == "__main__":
    # Parse arguments and start main()
    try:
        parser = argparse.ArgumentParser(
            description="Retrieves full match and summoner info.")
        parser.add_argument(
            "-k", "--key",
            help="developer or production key provided by Riot", nargs=1)
        parser.add_argument(
            "-r", "--region",
            help="server region for calls to the API",
            choices=REGIONS, required=True, nargs=1, type=str.upper)
        parser.add_argument(
            "-v", "--verbose",
            help="verbose (debug) output", action="store_true", default=False)

    except argparse.ArgumentError as e:
        logging.error("Invalid argument: {0}.".format(e.message))
        sys.exit(2)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            format='%(asctime)s: %(message)s',
            level=logging.DEBUG, datefmt='%d/%m/%Y %H:%M:%S')
    else:
        logging.basicConfig(
            format='%(asctime)s: %(message)s',
            level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S')

    parameters = {}

    # Initializes fundamental variables.
    # Initializes API key.
    if args.key is not None:
        logging.info("API key set by command-line argument.")
        parameters["key"] = args.key
    else:
        try:
            parameters["key"] = os.environ["API_KEY"]
            logging.info("API key set by environment variable DEV_KEY.")
        except KeyError:
            logging.error(
                "API key was not set. Set key with -k argument or set environment variable DEV_KEY.")
            sys.exit(2)

    # Initializes region.
    if args.region is None:
        logging.error("Region not set. Set region with -r argument.")
        sys.exit(2)
    else:
        logging.info("Region set to {0}.".format(args.region[0].upper()))
        parameters["region"] = args.region[0]

    # Calls main().
    main(parameters)
