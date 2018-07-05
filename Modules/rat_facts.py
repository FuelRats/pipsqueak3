"""
rat_facts.py - Managing Facts since 2018

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from utils.ratlib import Singleton
from Modules.database_manager import DatabaseManager
from Modules.context import Context
import re
import pyodbc
import datetime

internal_facts = ("!go", "!assign", "!add")  # any fact name in here will not be handled by the
                                             # handler


class Fact:
    name = None
    language = None
    message = None
    author = None
    # for SPARK-57
    timestamp = None

    def __init__(self, name: str, lang: str, message: str, author: str,
                 timestamp: datetime.datetime = None):
        self.name = name
        self.lang = lang
        self.message = message
        self.author = author
        self.timestamp = timestamp


class FactsManager(metaclass=Singleton):

    def __init__(self):
        """
        retrieves the DBM object. should this fail, it will set the variable to None,
            failing all subsequent calls
        """
        try:
            self.dbm = DatabaseManager()
        except pyodbc.Error:
            self.dbm = None

    async def get_fact(self, name: str, lang: str = "en") -> Fact or None:
        """
        retrieves a fact from the DB.
        Args:
            name: name of the fact to retrieve
            lang: language to retrieve

        Returns: message of the fact, or None should it not be found for the specified language

        """
        result = await self.dbm.select_rows("fact", "AND", {"lang": lang, "name": name})
        print(result)
        if result:
            return Fact(
                result[0][0],
                result[0][1],
                result[0][2],
                result[0][3]
                # FIXME: use timestamp once SPARK-57 is implemented
            )
        else:
            return None

    async def is_fact(self, name: str, lang: str = "en") -> bool:
        """
        checks for existence of a fact
        Args:
            name: name of the fact to check
            lang: language to check

        Returns: True if it exists, False otherwise

        """
        result = await self.dbm.select_rows("fact", "AND", {"lang": lang, "name": name})
        return len(result) > 0

    async def set_fact(self, fact: Fact) -> None:
        """
        sets a fact
        Args:
            fact (Fact): the fact to push into the DB
        Returns: None

        """
        if await self.is_fact(fact.name, fact.lang):
            await self.dbm.update_row("fact", "AND", {"message": fact.message}, {"name": fact.name,
                                                                                 "lang": fact.lang})
        else:
            await self.dbm.insert_row("fact", (fact.name, fact.lang, fact.message, fact.author))

    async def delete_fact(self, name: str, lang: str) -> None:
        """
        delete's the given fact
        Args:
            name: name of the fact to delete
            lang: language to delete

        Returns: None

        """
        await self.dbm.delete_row("fact", "AND", {"name": name, "lang": lang})

    async def handle_fact(self, context: Context) -> bool:
        regex = re.compile(r"!(?P<name>[a-zA-Z\d]+)-(?P<lang>[a-zA-Z]{2})|!(?P<name2>[a-zA-Z\d]+)")
        result = re.match(regex, context.words[0])

        if result is None:
            return False

        name = result.group("name")
        lang = None

        if not name:
            name = result.group("name2")
        else:
            lang = result.group("lang")

        if not lang:
            lang = "en"

        if name in internal_facts:
            return True
        if await self.is_fact(name, lang):
            message = (await self.get_fact(name, lang)).message
            context.reply(message)
            return True
        return False
