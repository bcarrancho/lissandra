import argparse
import asyncio
import logging
from pathlib import Path
import os
import signal
import sys

import aiohttp
import aiosqlite

import lissandra
from client import APIClient

lissandra.exiting = False

def main():
    try:
        parser = argparse.ArgumentParser(
            description="Retrieves full match and summoner info.")
        parser.add_argument(
            "-k", "--key",
            help="developer or production key provided by Riot", nargs=1)
        parser.add_argument(
            "-v", "--verbose",
            help="verbose (debug) output", action="store_true", default=False)
    except argparse.ArgumentError as e:
        logging.error("Invalid argument: {0}.".format(e.message))
        sys.exit(2)

    args = parser.parse_args()

    # Sets logging
    if args.verbose:
        logging.basicConfig(
            format='%(asctime)s: %(message)s',
            level=logging.DEBUG, datefmt='%d/%m/%Y %H:%M:%S')
    else:
        logging.basicConfig(
            format='%(asctime)s: %(message)s',
            level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S')
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Initializes fundamental variables
    # Initializes API key
    if args.key is not None:
        logging.info("API key set by command-line argument.")
        key = args.key
    else:
        try:
            key = os.environ["RIOT_API_KEY"]
            logging.info("API key set by environment variable DEV_KEY.")
        except KeyError:
            logging.error(
                "API key was not set. Set key with -k argument or set environment variable DEV_KEY.")
            sys.exit(2)


    parameters = {}
    parameters ["regions"] = ["BR", "EUNE", "EUW", "JP", "KR",
                              "LAN", "LAS", "NA", "OCE", "TR", "RU"]
    parameters["data_path"] = Path('.', 'data')
    parameters["key"] = key

    loop = asyncio.get_event_loop()

    # Sets signal handler
    loop.add_signal_handler(signal.SIGINT, shutdown)

    loop.run_until_complete(run(parameters))
    logging.info("Terminated")


async def run(parameters):
    loop = asyncio.get_event_loop()
    clients = {}
    async with aiohttp.ClientSession(loop=loop) as session:
        for region in parameters["regions"]:
            clients[region] = APIClient(
                region, session, parameters["key"], parameters["data_path"])
        # Await until ctrl+c
        while not lissandra.exiting:
            await asyncio.sleep(1)

        # Exiting, shutdown nicely
        for client in clients.values():
            client.exiting = True
        for client in clients.values():
            await client.shutdown.wait()

def shutdown():
    logging.info("Received shutdown signal")
    lissandra.exiting = True

if __name__ == "__main__":
    main()
