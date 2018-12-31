"""
fact_manager.py - Fact Management

Provides a context manager for manipulating, retrieving, and storing facts.
This class requires database.DatabaseManager and Modules.fact.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging

from Modules.fact import Fact
from database import DatabaseManager
from psycopg2 import sql

log = logging.getLogger(f"mecha.{__name__}")


class FactManager(object):

    _FACT_TABLE = 'fact2'

    _CREATE_SQL = ''
    _DEL_SQL = ''
    _FIND_SQL = ''
    _UPDATE_SQL = ''
    _HIST_SQL = ''

    # TODO: Context manager support
    # FIXME: Update table names for production database

    async def find(self, name: str, lang: str) -> Fact:
        """
        Queries the database for a fact, and returns a populated Fact object.
        Args:
            name: name of fact to search, ie. 'prep'
            lang: language ID for fact, defaults to 'en' (see Fact Class)

        Returns: Populated Fact Object

        """
        # Pass nothing to DBM, use config file values
        dbm = DatabaseManager()
        # Build SQL Object for our query
        query = sql.SQL(f"SELECT name, lang, message from "
                        f"{FactManager._FACT_TABLE} where name=%s AND lang=%s")

        rows = await dbm.query(query, (name, lang))
        result = Fact()

        # Unpack list, first checking if it is empty:
        if rows:
            result_tup = next(iter(rows or []))
            result.name, result.lang, result.message = result_tup

        return result

    async def add(self, fact: Fact):
        """
        Adds a new fact to the database.
        """

