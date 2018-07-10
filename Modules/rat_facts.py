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

internal_facts = ("!go", "!assign", "!add")
# any fact name in here will not be handled by the handler


class Fact:
    name = None
    language = None
    message = None
    author = None
    # for SPARK-57
    timestamp = None

    def __init__(self, name: str, lang: str, message: str, author: str,
                 timestamp: datetime.datetime):
        self.name = name
        self.lang = lang
        self.message = message
        self.author = author
        self.timestamp = timestamp


class FactsManager(metaclass=Singleton):

    @property
    def enabled(self):
        return self.dbm.enabled

    @enabled.setter
    def enabled(self, value):
        raise RuntimeError("You cant set this. Really. If you want me disable, disable the DBM.")

    def __init__(self):
        """
        retrieves the DBM object.
        """
        self.dbm = DatabaseManager()

    async def get_fact(self, name: str, lang: str = "en") -> Fact or None:
        """
        retrieves a fact from the DB.
        Args:
            name: name of the fact to retrieve
            lang: language to retrieve

        Returns: message of the fact, or None should it not be found for the specified language

        """
        result = await self.dbm.select_rows("fact", "AND", {"lang": lang, "name": name})
        timestamp = (await self.dbm.select_rows("fact_timestamps", "AND",
                                                {"lang": lang, "name": name}))
        if len(timestamp) > 0:
            timestamp = timestamp[0].last_modified
        else:
            timestamp = datetime.datetime.utcfromtimestamp(0)
        if result:
            result = result[0]
            return Fact(
                result[0],
                result[1],
                result[2],
                result[3],
                timestamp
            )
        else:
            return None

    async def is_fact(self, name: str, lang: str = "en") -> bool or None:
        """
        checks for existence of a fact
        Args:
            name: name of the fact to check
            lang: language to check

        Returns: True if it exists, False if it exists

        """
        result = await self.dbm.select_rows("fact", "AND", {"lang": lang, "name": name})
        return len(result) > 0

    async def set_fact(self, fact: Fact) -> bool or None:
        """
        sets a fact
        Args:
            fact (Fact): the fact to push into the DB
        Returns: True on success, False if it failed

        """
        try:
            await self.dbm.insert_row("fact", {"name": fact.name, "lang": fact.lang, "message": fact.message,
                                               "author": fact.author}, ("name", "lang",))
        except ValueError:
            return False
        else:
            time = datetime.datetime.now(tz=datetime.timezone.utc)
            self.dbm._execute(r"INSERT INTO fact_timestamps (name, lang, last_modified) "
                              r"VALUES("
                              f"'{fact.name}', '{fact.lang}', ?)"
                              r"ON CONFLICT (name, lang)"
                              r"DO UPDATE SET last_modified = ?",
                              time, time  # time is doubled on purpose
                              )
            return True

    async def delete_fact(self, name: str, lang: str) -> bool or None:
        """
        delete's the given fact
        Args:
            name: name of the fact to delete
            lang: language to delete

        Returns: True on success, False if it failed and None if the DBM is disabled

        """
        if not self.dbm.enabled:
            return None
        try:
            await self.dbm.delete_row("fact", "AND", {"name": name, "lang": lang})
            return True
        except ValueError:
            return False

    async def handle_fact(self, context: Context) -> bool:
        """

        Responds with the message of the fact, should a match be found and not listed as an
        internal fact.

        Args:
            context: the context as passed by rat_command

        Returns: True if it was a fact, False if not. Will also return False,
            should the DBM be disabled.

        """
        if not self.dbm.enabled:
            context.reply("Sadly, Facts are currently not available. Please check back later.")
            return False

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
