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
from typing import Dict
import datetime

internal_facts = ("!go", "!assign", "!add")
# any fact name in here will not be handled by the handler


class Fact:
    def __init__(self, name: str, lang: str, message: str, author: str,
                 timestamp: datetime.datetime):
        self._name = name
        self._lang = lang
        self._message = message
        self._author = author
        self._timestamp = timestamp

    @property
    def name(self) -> str:
        return self._name

    @property
    def lang(self) -> str:
        return self._lang

    @property
    def message(self) -> str:
        return self._message

    @property
    def author(self) -> str:
        return self._author

    @property
    def timestamp(self) -> datetime.datetime:
        return self._timestamp


class FactsManager(Singleton):

    @property
    def enabled(self):
        return self.dbm.enabled

    def __init__(self):
        """
        retrieves the DBM object.
        """
        self.dbm = DatabaseManager()

    async def get_fact(self, name: str, lang: str) -> Fact or None:
        """
        retrieves a fact from the DB.
        Args:
            name: name of the fact to retrieve
            lang: language to retrieve

        Returns: the Fact object, or None should it not be found for the specified language

        """
        # this is a intended apparent duplicate of is_fact

        result = await self.dbm.select_rows("fact", "AND", {"lang": lang, "name": name})
        timestamp = (
            await self.dbm.select_rows("fact_timestamps", "AND",
                                       {"lang": lang, "name": name} if lang is not None
                                       else {"name": name}
                                       )
        )

        if len(timestamp) > 0:
            timestamp = timestamp[-1].date_changed
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

    async def is_fact(self, name: str, lang: str = "en") -> bool:
        """
        checks for existence of a fact
        Args:
            name: name of the fact to check
            lang: language to check

        Returns: True if it exists, False if it does not exist

        """
        # this is a intended apparent duplicate of get_fact
        result = await self.dbm.select_rows("fact", "AND", {"lang": lang, "name": name})
        return len(result) > 0

    async def set_fact(self, fact: Fact) -> bool:
        """
        sets a fact
        Args:
            fact (Fact): the fact to push into the DB
        Returns: True on success, False if it failed

        """
        try:
            await self.dbm.insert_row("fact",
                                      {"name": fact.name,
                                       "lang": fact.lang,
                                       "message": fact.message,
                                       "author": fact.author},
                                      ("name", "lang",)
                                      )
        except ValueError:
            return False
        else:
            time = datetime.datetime.now(tz=datetime.timezone.utc)
            old_fact = await self.get_fact(fact.name, fact.lang)
            if old_fact.message == fact.message:
                self.dbm._execute(r"INSERT INTO fact_timestamps ("
                                  r"name, lang, message, author, date_changed) "
                                  r"VALUES("
                                  f" '{fact.name}',"
                                  f" '{fact.lang}',"
                                  f" '{old_fact.message}',"
                                  f" '{old_fact.author}', ?"
                                  f")",
                                  time
                                  )

            return True

    async def delete_fact(self, name: str, lang: str) -> bool:
        """
        delete's the given fact
        Args:
            name: name of the fact to delete
            lang: language to delete

        Returns: True on success, False otherwise

        """
        try:
            await self.dbm.delete_row("fact", "AND", {"name": name, "lang": lang})
            return True
        except ValueError:
            return False

    async def handle_fact(self, context: Context) -> bool:
        """

        Responds in IRC with the message of the fact, should a match be found and not listed as an
        internal fact.

        Args:
            context: the context as passed by rat_command

        Returns: True if it was a fact, False if not. Will also return False,
            should the DBM be disabled.

        """
        if not self.dbm.enabled:
            await context.reply("Sadly, Facts are currently not available. Please check back later.")
            return False

        if not isinstance(context, Context):
            raise ValueError(f"Context was of type {type(context)}, which is not permitted.")

        regex = re.compile(r"(?P<name>[a-zA-Z\d]+)-(?P<lang>[a-zA-Z]{2})|(?P<name2>[a-zA-Z\d]+)")
        # Tries to split the inputted word (e.g test-tr)
        # (prefix has already been removed at context creation time)
        # into a group called "name" and a group called "lang".
        # Should this fail, for example because no language has been supplied,
        # it'll store the name of the fact in a group called "name2"

        result = re.match(regex, context.words[0])

        if result is None:
            return False

        name = result.group("name")
        lang = None

        if name is None:
            name = result.group("name2")
        else:
            lang = result.group("lang")

        if lang is None:
            lang = "en"

        if name in internal_facts:
            return True

        if await self.is_fact(name, lang):
            message = (await self.get_fact(name, lang)).message
            await context.reply(message)
            return True
        return False
