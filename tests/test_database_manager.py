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


@pytest.fixture(scope="class")
def dropTables():
    """
    Drops all the tables
    :return:
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
            DatabaseManager().cursor.execute(f"DROP TABLE {name}")
        except (pyodbc.ProgrammingError, pyodbc.OperationalError, pyodbc.DataError):
            pass


# noinspection PyProtectedMember
@pytest.mark.useFixture("dropTables")
class TestStuff(object):
    manager = DatabaseManager()

    async def test_has_table(self):
        if await self.manager.has_table("testtablehas"):
            await self.manager.drop_table("testtablehas")
        assert not await self.manager.has_table("testtablehas")
        await self.manager.create_table("testtablehas", {"string1": "VARCHAR"})
        assert await self.manager.has_table("testtablehas")

    async def test_select_row(self):
        if not await self.manager.has_table("testtableselect"):
            await self.manager.create_table("testtableselect", {"string1": "VARCHAR"})
        await self.manager.insert_row("testtableselect", ("thest",))

        tmp = await self.manager.select_rows("testtableselect", "AND", {"string1": "thest"})
        print(tmp)
        assert tmp[0][0] == ("thest",)[0]

    async def test_create_table(self):
        if await self.manager.has_table("testtablecreate"):
            await self.manager.drop_table("testtablecreate")
        if not await self.manager.has_table("testtablecreate"):
            await self.manager.create_table("testtablecreate", {"string1": "VARCHAR"})
        with pytest.raises(ValueError):
            await self.manager.create_table("testtablecreate", {"test": "VARCHAR"})

    async def test_insert_row(self):
        if not await self.manager.has_table("testtableinsert"):
            await self.manager.create_table("testtableinsert", {"string1": "VARCHAR"})
        await self.manager.insert_row("testtableinsert", ("test",))
        tmp = await self.manager.select_rows("testtableinsert", "AND", {"string1": "test"})
        assert tmp[0][0] == ("test",)[0]
        
        # with pytest.raises(OperationalError):
        #    await self.int_manager._insert_row("testtableinsert", ("test", "test2"))

    async def test_update_row(self):
        if not await self.manager.has_table("testtableupdate"):
            await self.manager.create_table("testtableupdate", {"string1": "VARCHAR"})
        await self.manager.insert_row("testtableupdate", ("thest",))
        await self.manager.update_row("testtableupdate", "AND", {"string1": "FizzBuzz"},
                                      {"string1": "thest"})

        tmp = await self.manager.select_rows("testtableupdate", "AND", {"string1": "FizzBuzz"})
        assert tmp[0][0] == "FizzBuzz"

    async def test_delete_row(self):
        if not await self.manager.has_table("testtabledelete"):
            await self.manager.create_table("testtabledelete", {"string1": "VARCHAR"})
        await self.manager.insert_row("testtabledelete", ("thest",))
        await self.manager.delete_row("testtabledelete", "AND", {"string1": "thest"})
        tmp = await self.manager.select_rows("testtabledelete", "AND", {"string1": "thest"})
        assert len(tmp) == 0
