"""
test_database_manager.py - UT for the databaseManager

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import pytest, pytest_asyncio, pyodbc
from Modules.database_manager import DatabaseManager

pytestmark = pytest.mark.asyncio


# noinspection PyProtectedMember
class TestStuff(object):
    manager = DatabaseManager()

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        table_names = ("testtablehas",
                       "testtableselect",
                       "testtablecreate",
                       "testtableinsert",
                       "testtableupdate",
                       "testtabledelete",
                       )
        for name in table_names:
            try:
                cls.manager.cursor.execute(f"DROP TABLE {name}")
            except (pyodbc.ProgrammingError, pyodbc.OperationalError, pyodbc.DataError):
                pass

    async def test_has_table(self):
        if await self.manager._has_table("testtablehas"):
            await self.manager._drop_table("testtablehas")
        assert not await self.manager._has_table("testtablehas")
        await self.manager._create_table("testtablehas", {"string1": "VARCHAR"})
        assert await self.manager._has_table("testtablehas")

    async def test_select_row(self):
        if not await self.manager._has_table("testtableselect"):
            await self.manager._create_table("testtableselect", {"string1": "VARCHAR"})
        await self.manager._insert_row("testtableselect", ("thest",))

        tmp = await self.manager._select_rows("testtableselect", "AND", {"string1": "thest"})
        print(tmp)
        assert tmp[0][0] == ("thest",)[0]

    async def test_create_table(self):
        if await self.manager._has_table("testtablecreate"):
            await self.manager._drop_table("testtablecreate")
        if not await self.manager._has_table("testtablecreate"):
            await self.manager._create_table("testtablecreate", {"string1": "VARCHAR"})
        with pytest.raises(ValueError):
            await self.manager._create_table("testtablecreate", {"test": "VARCHAR"})

    async def test_insert_row(self):
        if not await self.manager._has_table("testtableinsert"):
            await self.manager._create_table("testtableinsert", {"string1": "VARCHAR"})
        await self.manager._insert_row("testtableinsert", ("test",))

        # with pytest.raises(OperationalError):
        #    await self.int_manager._insert_row("testtableinsert", ("test", "test2"))

        if await self.manager._has_table("testtableinsert"):
            await self.manager._drop_table("testtableinsert")

    async def test_update_row(self):
        if not await self.manager._has_table("testtableupdate"):
            await self.manager._create_table("testtableupdate", {"string1": "VARCHAR"})
        await self.manager._insert_row("testtableupdate", ("thest",))
        await self.manager._update_row("testtableupdate", "AND", {"string1": "FizzBuzz"},
                                       {"string1": "thest"})

        assert \
            (await self.manager._select_rows("testtableupdate", "AND", {"string1": "FizzBuzz"}))\
            [0][0] == "FizzBuzz"

    async def test_delete_row(self):
        if not await self.manager._has_table("testtabledelete"):
            await self.manager._create_table("testtabledelete", {"string1": "VARCHAR"})
        await self.manager._insert_row("testtabledelete", ("thest",))
        await self.manager._delete_row("testtabledelete", "AND", {"string1": "thest"})
        tmp = await self.manager._select_rows("testtabledelete", "AND", {"string1": "thest"})
        assert len(tmp) == 0
