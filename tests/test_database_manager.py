"""
test_database_manager.py - UT for the databaseManager

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import pytest
import pyodbc
from Modules.database_manager import DatabaseManager


@pytest.fixture(scope="session")
def prepare_dbm(dbm_fx):
    """
    Drops all the tables
    """
    #yield
    table_names = ("testtablehas",
                   "testtableselect",
                   "testtablecreate",
                   "testtableinsert",
                   "testtableupdate",
                   "testtabledelete",
                   )
    for name in table_names:
        try:
            dbm_fx.cursor.execute(f"DROP TABLE {name};")
        except (pyodbc.ProgrammingError, pyodbc.OperationalError, pyodbc.DataError):
            raise


# noinspection PyProtectedMember
@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.usefixtures("prepare_dbm")
class TestStuff(object):
    #manager = DatabaseManager()

    async def test_has_table(self, dbm_fx):
        if await dbm_fx.has_table("testtablehas"):
            await dbm_fx.drop_table("testtablehas")
        assert not await dbm_fx.has_table("testtablehas")
        await dbm_fx.create_table("testtablehas", {"string1": "VARCHAR"})
        assert await dbm_fx.has_table("testtablehas")

    async def test_select_row(self, dbm_fx):
        if not await dbm_fx.has_table("testtableselect"):
            await dbm_fx.create_table("testtableselect", {"string1": "VARCHAR"})
        await dbm_fx.insert_row("testtableselect", ("thest",))

        tmp = await dbm_fx.select_rows("testtableselect", "AND", {"string1": "thest"})
        print(tmp)
        assert tmp[0][0] == ("thest",)[0]

    async def test_create_table(self, dbm_fx):
        if await dbm_fx.has_table("testtablecreate"):
            await dbm_fx.drop_table("testtablecreate")
        if not await dbm_fx.has_table("testtablecreate"):
            await dbm_fx.create_table("testtablecreate", {"string1": "VARCHAR"})
        with pytest.raises(ValueError):
            await dbm_fx.create_table("testtablecreate", {"test": "VARCHAR"})

    async def test_insert_row(self, dbm_fx):
        if not await dbm_fx.has_table("testtableinsert"):
            await dbm_fx.create_table("testtableinsert", {"string1": "VARCHAR"})
        await dbm_fx.insert_row("testtableinsert", ("test",))
        tmp = await dbm_fx.select_rows("testtableinsert", "AND", {"string1": "test"})
        assert tmp[0][0] == ("test",)[0]

    async def test_update_row(self, dbm_fx):
        if not await dbm_fx.has_table("testtableupdate"):
            await dbm_fx.create_table("testtableupdate", {"string1": "VARCHAR"})
        await dbm_fx.insert_row("testtableupdate", ("thest",))
        await dbm_fx.update_row("testtableupdate", "AND", {"string1": "FizzBuzz"},
                                      {"string1": "thest"})

        tmp = await dbm_fx.select_rows("testtableupdate", "AND", {"string1": "FizzBuzz"})
        assert tmp[0][0] == "FizzBuzz"

    async def test_delete_row(self, dbm_fx):
        if not await dbm_fx.has_table("testtabledelete"):
            await dbm_fx.create_table("testtabledelete", {"string1": "VARCHAR"})
        await dbm_fx.insert_row("testtabledelete", ("thest",))
        await dbm_fx.delete_row("testtabledelete", "AND", {"string1": "thest"})
        tmp = await dbm_fx.select_rows("testtabledelete", "AND", {"string1": "thest"})
        assert len(tmp) == 0
