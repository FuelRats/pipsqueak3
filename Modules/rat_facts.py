"""
rat_facts.py - facts manager

Manages Facts

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""

from utils.ratlib import Singleton
from Modules.database_manager import DatabaseManager


class FactsManager(metaclass=Singleton):
    dbm = DatabaseManager()
    facts_table_name = "fact"

    async def get_fact(self, name: str, language: str = "en") -> dict or None:
        result = await self.dbm.select_rows(self.facts_table_name, "OR",
                                            {"name": name, "lang": language})
        if len(result) == 0:
            result = await self.dbm.select_rows(self.facts_table_name, "OR",
                                                {"name": "name", "lang": "en"})
        if len(result) == 0:
            return None
        return {"message": result[0][2], "lang": result[0][1]}
