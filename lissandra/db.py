import asyncio
import logging
import sqlite3

import aiosqlite

class BaseDB(object):
    def __init__(self, fname):
        self.fname = fname
        self.loop = asyncio.get_event_loop()
        self.init_db()


class SQLiteDB(BaseDB):
    async def empty_table(self, table_name):
        async with aiosqlite.connect(str(self.fname)) as db:
            query = 'DELETE FROM "' + table_name + '"'
            cursor = await db.execute(query)
            return cursor.rowcount if cursor is not None else None
            
    async def count(self, table_name):
        async with aiosqlite.connect(str(self.fname)) as db:
            query = 'SELECT COUNT(*) FROM "' + table_name + '"'
            cursor = await db.execute(query)
            if cursor is not None:
                res = await cursor.fetchone()
            return res[0] if cursor is not None else None


class DBMatch(SQLiteDB):
    def init_db(self):
        if not self.fname.is_file():
            conn = sqlite3.connect(str(self.fname))
            c = conn.cursor()
            c.execute("CREATE TABLE MatchDiscovered (matchId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE);")
            c.execute("CREATE TABLE MatchQueued (matchId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE);")
            c.execute("CREATE TABLE MatchFlushed (matchId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE);")
            c.execute("CREATE TABLE MatchError (matchId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE, httpCode INTEGER, timestamp BIGINT);")
            conn.commit()
            conn.close()
        else:
            self.loop.create_task(self.empty_table("MatchQueued"))
            logging.warning("Cleaning MatchFlushed Table")


class DBMatchlist(SQLiteDB):
    def init_db(self):
        if not self.fname.is_file():
            conn = sqlite3.connect(str(self.fname))
            c = conn.cursor()
            c.execute("CREATE TABLE MatchlistDiscovered (summonerId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE);")
            c.execute("CREATE TABLE MatchlistQueued (summonerId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE);")
            c.execute("CREATE TABLE MatchlistFlushed (summonerId BIGINT PRIMARY KEY DESC ON CONFLICT REPLACE, timestamp BIGINT);")
            c.execute("CREATE TABLE MatchlistError (summonerId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE, httpCode INTEGER, timestamp BIGINT, matchCount INTEGER);")
            conn.commit()
            conn.close()
        else:
            self.loop.create_task(self.empty_table("MatchlistQueued"))
            logging.warning("Cleaning MatchlistFlushed Table")


class DBSummoner(SQLiteDB):
    def init_db(self):
        if not self.fname.is_file():
            conn = sqlite3.connect(str(self.fname))
            c = conn.cursor()
            c.execute("CREATE TABLE SummonerDiscovered (accountId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE);")
            c.execute("CREATE TABLE SummonerQueued (accountId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE);")
            c.execute("CREATE TABLE SummonerFlushed (accountId BIGINT PRIMARY KEY DESC ON CONFLICT REPLACE, timestamp BIGINT);")
            c.execute("CREATE TABLE SummonerError (accountId BIGINT PRIMARY KEY DESC ON CONFLICT IGNORE, httpCode INTEGER, timestamp BIGINT, matchCount INTEGER);")
            conn.commit()
            conn.close()
        else:
            self.loop.create_task(self.empty_table("SummonerQueued"))
            logging.warning("Cleaning SummonerFlushed Table")
