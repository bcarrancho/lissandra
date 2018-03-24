import logging
import sqlite3
import pathlib

import aiosqlite


class DBMatch(object):
    def __init__(self, fname):
        self.fname = fname
        self.init_db()

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


class DBMatchlist(object):
    def __init__(self, fname):
        self.fname = fname
        self.init_db()

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
