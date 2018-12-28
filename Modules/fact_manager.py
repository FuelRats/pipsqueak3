"""
fact_manager.py - Fact Management

Provides a context manager for manipulating, retrieving, and storing facts.
This module depends on database.DatabaseManager, and a database connection.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging
from database import DatabaseManager
from psycopg2 import sql


log = logging.getLogger(f"mecha.{__name__}")


class Fact(object):
    def __init__(self, name=None, lang='en', message=None):
        self._name = name
        self._lang = lang
        self._message = message

    @property
    def name(self) -> str:
        """
        Name of fact, ie 'prep'
        Returns: name of fact
        """
        return self._name

    @property
    def lang(self) -> str:
        """
        language code, ie 'en'
        Returns: language of fact.

        This may be may be longer than two, in the case of template facts.
        """
        return self._lang

    @property
    def message(self) -> str:
        """
        Message for fact - the set content.
        Returns: str fact content
        """
        return self._message

    @name.setter
    def name(self, value: str):
        """
        Sets fact name.
        Args:
            value: str
        Returns: Nothing.
        """
        if not isinstance(value, str):
            raise TypeError("Fact.name must be of string type.")

        self._name = value

    @lang.setter
    def lang(self, value: str):
        """
        Sets fact language ID.
        Args:
            value: str language ID
        Returns: Nothing
        """
        if not isinstance(value, str):
            raise TypeError("Fact.lang must be of string type.")

        self._lang = value

    @message.setter
    def message(self, value: str):
        """
        Sets the returned message for the fact
        Args:
            value: str fact message
        Returns: Nothing
        """

        if not isinstance(value, str):
            raise TypeError("Fact.message must be of string type.")

        self._message = value


class FactManager(object):

    # TODO: Context manager support

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
        query = sql.SQL("SELECT name, lang, message from fact where name=%s AND lang=%s")

        rows = await dbm.query(query, (name, lang))
        result = Fact()

        # Unpack list, first checking if it is empty:
        if rows:
            result_tup = next(iter(rows or []))
            result.name, result.lang, result.message = result_tup

        return result

    async def modify(self, fact: Fact, attribute: str, value: str):
        """
        Change a property of a fact, and commit to the database.
        Args:
            fact: Fact object to be modified
            attribute: name, author, etc to be modified.
            value: new value.

        Returns: Nothing

        """
        pass
