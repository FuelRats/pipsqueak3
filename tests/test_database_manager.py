"""
test_database_manager.py - UT for the databaseManager

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
from unittest import TestCase, skip
from Modules.database_manager import DataBaseManager


class TestDB(TestCase):
    def setUp(self):
        """
        set up manager and int_manager vars.
        Returns: None

        """
        self.manager = DataBaseManager(":memory:")  # use temporary RAM-DB
        self.int_manager = self.manager.instance

    def test_has_table(self):
        if self.int_manager._has_table("testTableHas"):
            self.int_manager.connection.execute("DROP TABLE 'testTableHas'")
        self.int_manager._create_table("testTableHas", {"string1": "STRING"})
        self.assertTrue(self.int_manager._has_table("testTableHas"))

    def test_create_table(self):
        if self.int_manager._has_table("testTableCreate"):
            self.int_manager.connection.execute("DROP TABLE 'testTableCreate'")
        self.int_manager._create_table("testTableCreate", {"string1": "STRING"})
        with self.assertRaises(ValueError):
            self.int_manager._create_table("testTableCreate", {"test": "STRING"})

    def test_insert_row(self):
        if not self.int_manager._has_table("testTableInsert"):
            self.int_manager._create_table("testTableInsert", {"string1": "STRING"})
        self.int_manager._insert_row("testTableInsert", ("test",))
#        with self.assertRaises(sqlite3.OperationalError):
#            self.int_manager._insert_row("testTableInsert", ("test", 0))
        if self.int_manager._has_table("testTableInsert"):
            self.int_manager.connection.execute("DROP TABLE 'testTableInsert'")
        with self.assertRaises(ValueError):
            self.int_manager._insert_row("testTableInsert", ("test",))

    def test_select_row(self):
        if not self.int_manager._has_table("testTableSelect"):
            self.int_manager._create_table("testTableSelect", {"string1": "STRING"})
            self.int_manager._insert_row("testTableSelect", ("thest",))
        self.assertEqual(self.int_manager._select_rows("testTableSelect", "AND", {"string1": "thest"})[0], ("thest",))


    def test_update_row(self):
        if not self.int_manager._has_table("testTableUpdate"):
            self.int_manager._create_table("testTableUpdate", {"string1": "STRING"})
            self.int_manager._insert_row("testTableUpdate", ("thest",))
        self.int_manager._update_row("testTableUpdate", "AND", {"string1": "FizzBuzz"},
                                     {"string1": "thest"})
        self.assertEqual(self.int_manager._select_rows("testTableUpdate", "AND", {"string1": "FizzBuzz"}),
                         [("FizzBuzz",)])

    def test_delete_row(self):
        if not self.int_manager._has_table("testTableDelete"):
            self.int_manager._create_table("testTableDelete", {"string1": "STRING"})
            self.int_manager._insert_row("testTableDelete", ("thest",))
        self.int_manager._delete_row("testTableDelete", "AND", {"string1": "thest"})
        self.assertEqual(
            len(self.int_manager._select_rows("testTableDelete", "AND", {"string1": "thest"})), 0)
