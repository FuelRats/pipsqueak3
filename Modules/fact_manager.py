"""
fact_manager.py - Fact Management

Provides a context manager for manipulating, retrieving, and storing facts.
This class requires database.DatabaseManager and Modules.fact.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import datetime
import logging
from enum import Enum

import psycopg2
from psycopg2 import sql
from datetime import timezone
from Modules.fact import Fact
from database import DatabaseManager

log = logging.getLogger(f"mecha.{__name__}")


class FactManager(DatabaseManager):
    class Action(Enum):
        ADD = 1
        REMOVE = 0

    # Name of tables, for DBM
    _FACT_TABLE = 'fact2'
    _FACT_HISTORY = 'fact_history'

    def __init__(self):
        log.info("Fact Manager Initialized.")
        super().__init__()

    # TODO: Context manager support

    async def find(self, name: str, lang: str) -> Fact:
        """
        Queries the database for a fact, and returns a populated Fact object.
        Args:
            name: name of fact to search, ie. 'prep'
            lang: language ID for fact, defaults to 'en' (see Fact Class)

        Returns: Populated Fact Object

        """
        # Build SQL Object for our query
        query = sql.SQL(f"SELECT name, lang, message, aliases, author, edited, editedby, mfd from "
                        f"{FactManager._FACT_TABLE} where name=%s AND lang=%s")

        rows = await self.query(query, (name, lang))

        return Fact(*rows[0]) if rows else Fact()

    async def add(self, fact: Fact):
        """
        Adds a new fact to the database.  This will result in a ProgrammingError being thrown
        if a fact added this way violates the name, lang PK relationship.  Verify a fact
        does NOT exist before adding to avoid this.

        Aliases cannot be inserted this way, at this time.  None is forced for fact.aliases.
        """
        add_query = sql.SQL(f"INSERT INTO {FactManager._FACT_TABLE} "
                            f"VALUES ( %s, %s, %s, %s, %s, %s, %s, %s )")

        try:
            if fact.complete:
                add_values = (fact.name, fact.lang, fact.message, None,
                              fact.author, fact.edited, fact.editedby, fact.mfd)
                await self.query(add_query, add_values)
            else:
                raise TypeError("Attempted commit on incomplete Fact.")
        except (psycopg2.DatabaseError, psycopg2.ProgrammingError) as error:
            log.exception(f"Unable to add fact '{fact.name}!", error)
            raise error

    async def delete(self, name: str, lang: str):
        """
        Deletes a fact from the database.  This is an un-recoverable action.
        Raises if performed on a fact not marked for deletion.
        Args:
            name: name of fact to be deleted
            lang: langID of fact to be deleted

        Returns: Nothing
        """
        del_query = sql.SQL(f"DELETE FROM {FactManager._FACT_TABLE} WHERE name=%s AND lang=%s")

        fact = await self.find(name, lang)
        log.info(f"Fact MFD is {fact.mfd}")
        if fact.mfd:
            try:
                await self.query(del_query, (name, lang))
            except psycopg2.ProgrammingError:
                log.exception("Unable to delete fact row from database.")
        else:
            raise psycopg2.ProgrammingError(f"{name}-{lang} is not marked for deletion.")

    async def exists(self, name: str, lang: str) -> bool:
        """
        Quick True/False return if a fact with that combo already exists.
        Args:
            name: name of fact
            lang: language ID of fact

        Returns: True/False, if already exists.

        """
        query = sql.SQL(f"SELECT COUNT(*) message FROM "
                        f"{FactManager._FACT_TABLE} WHERE name=%s AND lang=%s")

        qresult = await self.query(query, (name, lang))

        return qresult[0][0]

    async def mfd(self, name: str, lang: str) -> bool:
        """
        Toggles the MFD flag on a fact.
        Args:
            name: name of fact to update
            lang: lang of fact to update

        Returns: True/False that fact was set to.
        """
        query = sql.SQL(f"SELECT fact2.mfd FROM "
                        f"{FactManager._FACT_TABLE} WHERE name=%s AND lang=%s")
        qresult = await self.query(query, (name, lang))

        # Set MFD to inverted value of qresult
        mfd_query = sql.SQL(f"UPDATE {FactManager._FACT_TABLE} "
                            f"SET mfd=%s WHERE name=%s AND lang=%s")
        mfd_value = not qresult[0][0]
        await self.query(mfd_query, (mfd_value, name, lang))

        return mfd_value

    async def mfd_list(self, numresults=5) -> list:
        """
        Returns a list of facts marked for deletion

        Returns: list of facts
        Example: ['test-en', 'prep-en', 'mfdtest-en']
        """
        query = sql.SQL(f"SELECT name, lang FROM "
                        f"{FactManager._FACT_TABLE} WHERE mfd=%s "
                        f"ORDER BY edited DESC LIMIT {numresults}")
        raw_results = await self.query(query, (True,))
        result = []

        result = [f"{item[0]}-{item[1]}" for item in raw_results]

        return result

    async def log(self, fact_name: str, fact_lang: str, author: str, msg: str,
                  new_field=None, old_field=None):
        """
        Writes a transaction log entry to the transaction log table.
        Args:
            fact_name: Name of fact this applies to.
            fact_lang: langID of fact this applies to.
            author: the user that triggered the log entry.
            msg: Message to be written to log.
            new_field: Contents to place in the 'new' field for the log row.
            old_field: Contents to place in the 'old' field for the log row.

        Returns: Nothing.
        """
        log_query = sql.SQL(f"INSERT INTO fact_transaction VALUES "
                            f"(DEFAULT, %s, %s, %s, %s, %s, %s, %s)")
        query_data = (fact_name, fact_lang, author, msg, old_field, new_field,
                      datetime.datetime.now(tz=timezone.utc))
        try:
            await self.query(log_query, query_data)
        except psycopg2.ProgrammingError as error:
            log.exception("Unable to write transaction log to table.")
            raise error

    async def facthistory(self, fact_name: str, fact_lang: str) -> list:
        """
        Pulls the last 5 transaction logs for a fact, as a tuple
        Args:
            fact_name: Name of the fact
            fact_lang: LangID of the fact.

        Returns: tuple of transaction log items, for fact.
        """
        query = sql.SQL(f"SELECT name, lang, author, message, ts, old, new "
                        f"FROM fact_transaction WHERE name=%s AND lang=%s ORDER BY ts DESC LIMIT 5")
        query_data = (fact_name, fact_lang)
        result = await self.query(query, query_data)

        return result
