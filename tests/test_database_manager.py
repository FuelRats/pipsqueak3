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


@pytest.fixture
def prepare_dbm(dbm_fx: DatabaseManager):
    """
    Drops all the tables
    """
    if dbm_fx.marker is not None:
        return
    dbm_fx.marker = False
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
            pass


# noinspection PyProtectedMember
@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.usefixtures("prepare_dbm")
class TestStuff(object):

    @pytest.mark.skip(reason="Not a test")
    def finalize(self, dbm_fx):
        dbm_fx.enabled = False

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

        assert (await dbm_fx.select_rows("testtableselect", "AND", {"string1": "thest"}))[0][0]\
            == ("thest",)[0]

    async def test_create_table(self, dbm_fx):
        if await dbm_fx.has_table("testtablecreate"):
            await dbm_fx.drop_table("testtablecreate")
        if not await dbm_fx.has_table("testtablecreate"):
            await dbm_fx.create_table("testtablecreate", {"string1": "VARCHAR"})
        with pytest.raises(ValueError):
            await dbm_fx.create_table("testtablecreate", {"test": "VARCHAR"})

    async def test_drop_table(self, dbm_fx: DatabaseManager):
        if not await dbm_fx.has_table("testtabledrop"):
            await dbm_fx.create_table("testtabledrop", {"string1": "TIMESTAMP"})
        assert await dbm_fx.has_table("testtabledrop")
        await dbm_fx.drop_table("testtabledrop")
        assert not await dbm_fx.has_table("testtabledrop")

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

    async def test_double_dash_checks(self, dbm_fx: DatabaseManager):
        with pytest.raises(ValueError):
            await dbm_fx.delete_row("testtabledelete", "AND", {"test": "OR TRUE; -- "})
            await dbm_fx.update_row("testtableupdate", "AND", {"string1": " OR FALSE; -- "})
            await dbm_fx.insert_row("testtableinsert", ("stuff", "more stuff", "DIE; -- "))
            await dbm_fx.select_rows("testtableselect", "AND", {"test; -- ": "stuff"})

        try:
            await dbm_fx.delete_row("testtabledelete", "AND", {"test": "OR TRUE; -- "}, True)
            await dbm_fx.update_row("testtableupdate", "AND", {"string1": " OR FALSE; -- "}, None, True)
            await dbm_fx.insert_row("testtableinsert", ("stuff", "more stuff", "DIE; -- "), True)
            await dbm_fx.select_rows("testtableselect", "AND", {"test; -- ": "stuff"}, True)
        except pyodbc.Error:
            pass

    @pytest.mark.last
    async def test_connection_error_handling(self, dbm_fx):
        # disable the module, causing it to disconnect
        dbm_fx.enabled = False

        # this raises as we invoke it while it is disconnected
        with pytest.raises(RuntimeError):
            await dbm_fx.select_rows("testtableselect", "AND", {"string1": "thest"})

        # now we reconnect
        dbm_fx.enabled = True

        # this should work now, as we reconnected
        await dbm_fx.select_rows("testtableselect", "AND", {"string1": "thest"})

        # now we bypass the shutdown code and close the connection()
        dbm_fx.connection.close()

        # this won't fail as it reconnects
        await dbm_fx.select_rows("testtableselect", "AND", {"string1": "thest"})

        # bodge fix: call teardown after this test, as its always being the last one
        self.finalize(dbm_fx)

