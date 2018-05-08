"""
test_database_manager.py - UT for the databaseManager

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import pytest, pytest_asyncio, aiosqlite
from Modules.database_manager import DataBaseManager

pytestmark = pytest.mark.asyncio


# noinspection PyProtectedMember
class TestStuff(object):
    file_path = "test.db"
    manager = DataBaseManager(file_path)  # use temporary RAM-DB
    int_manager = manager._DataBaseManager__instance

    async def test_has_table(self):
        if await self.int_manager._has_table("testTableHas"):
            async with aiosqlite.connect(self.file_path) as db:
                await db.execute("DROP TABLE 'testTableHas'")
                await db.commit()
        assert not await self.int_manager._has_table("testTableHas")
        await self.int_manager._create_table("testTableHas", {"string1": "STRING"})
        assert await self.int_manager._has_table("testTableHas")

    async def test_select_row(self):
        if not await self.int_manager._has_table("testTableSelect"):
            await self.int_manager._create_table("testTableSelect", {"string1": "STRING"})
        await self.int_manager._insert_row("testTableSelect", ("thest",))

        tmp = await self.int_manager._select_rows("testTableSelect", "AND", {"string1": "thest"})
        print(tmp)
        assert tmp[0] == ("thest",)

    async def test_create_table(self):
        if await self.int_manager._has_table("testTableCreate"):
            async with aiosqlite.connect(self.file_path) as db:
                await db.execute("DROP TABLE 'testTableCreate'")
                await db.commit()
        await self.int_manager._create_table("testTableCreate", {"string1": "STRING"})
        with pytest.raises(ValueError):
            await self.int_manager._create_table("testTableCreate", {"test": "STRING"})

    async def test_insert_row(self):
        if not await self.int_manager._has_table("testTableInsert"):
            await self.int_manager._create_table("testTableInsert", {"string1": "STRING"})
        await self.int_manager._insert_row("testTableInsert", ("test",))

        # with pytest.raises(OperationalError):
        #    await self.int_manager._insert_row("testTableInsert", ("test", "test2"))

        if await self.int_manager._has_table("testTableInsert"):
            async with aiosqlite.connect(self.file_path) as db:
                await db.execute("DROP TABLE 'testTableInsert'")
                await db.commit()
        with pytest.raises(ValueError):
            await self.int_manager._insert_row("testTableInsert", ("test",))

    async def test_update_row(self):
        if not await self.int_manager._has_table("testTableUpdate"):
            await self.int_manager._create_table("testTableUpdate", {"string1": "STRING"})
        await self.int_manager._insert_row("testTableUpdate", ("thest",))
        await self.int_manager._update_row("testTableUpdate", "AND", {"string1": "FizzBuzz"},
                                           {"string1": "thest"})

        assert\
            await self.int_manager._select_rows("testTableUpdate", "AND", {"string1": "thest"})\
        == [("FizzBuzz",)]

    async def test_delete_row(self):
        if not await self.int_manager._has_table("testTableDelete"):
            await self.int_manager._create_table("testTableDelete", {"string1": "STRING"})
        await self.int_manager._insert_row("testTableDelete", ("thest",))
        await self.int_manager._delete_row("testTableDelete", "AND", {"string1": "thest"})
        tmp = await self.int_manager._select_rows("testTableDelete", "AND", {"string1": "thest"})
        assert len(tmp) == 0


