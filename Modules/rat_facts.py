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


class FactsManager(metaclass=Singleton):

    def __init__(self):
        """
        retrieves the DBM object. should this fail, it will set the variable to None,
            failing all subsequent calls
        """
        try:
            self.dbm = DatabaseManager()
        except:
            self.dbm = None

    async def get_fact(self, name: str, lang: str = "en") -> str or None:
        """
        retrieves a fact from the DB.
        Args:
            name: name of the fact to retrieve
            lang: language to retrieve

        Returns: message of the fact, or None should it not be found for the specified language

        """
        result = await self.dbm.select_rows("fact", "AND", {"lang": lang, "name": name})
        if result:
            return result[0][2]
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

    async def set_fact(self, name: str, message: str, author: str, lang: str = "en") -> None:
        """
        sets a fact
        Args:
            name: name of the fact to set
            message: response of the fact
            author: name of the rat responsible for the change/Addition
            lang: language of the fact

        Returns: None

        """
        if await self.is_fact(name, lang):
            await self.dbm.update_row("fact", "AND", {"message": message}, {"name": name, "lang": lang})
        else:
            await self.dbm.insert_row("fact", (name, lang, message, author))

    async def delete_fact(self, name: str, lang: str) -> None:
        """
        delete's the given fact
        Args:
            name: name of the fact to delete
            lang: language to delete

        Returns: None

        """
        await self.dbm.delete_row("fact", "AND", {"name": name, "lang": lang})
