"""
database_manager.py - Manages access to the central database file

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import aiosqlite
import config


class DataBaseManager:
    __instance = None

    def __init__(self, file_name: str = config.DataBaseManager.default_file_name):
        """
        Creates the master instance of the nested singleton class
        """
        if not self.__instance:
            self.__instance = self.__DatabaseManager(file_name)

    class __DatabaseManager:
        """
        Nested class, singleton
        Does all the access magic
        """

        def __init__(self, file_name: str):
            """
            Initializes the connection and creates the default tables, should they not exist
            """
            self.filePath = file_name
            self.connection = aiosqlite.connect(self.filePath)
            if self._has_table("mecha3-facts"):
                self._create_table("mecha3-facts", {"fact": "STRING", "lang": "STRING", "text": "STRING"})

        async def _has_table(self, name: str):
            """

            Args:
                name (str): name of the table to check

            Returns: True when table exists, false otherwise

            """
            result = None
            async with aiosqlite.connect(self.filePath) as db:
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
                result = await cursor.fetchone()
                await cursor.close()
            return result is not None


        async def _create_table(self, name: str, types: dict):
            """
            Creates the table with the given name and columns
            Args:
                name (str): name of the table to create
                types (dict): dict of columns, key denotes the name, value the type.
                    type must be a valid SQL type

            Returns: None
            """
            if await self._has_table(name):
                raise ValueError(f"Table {name} already exists")
            type_string: str = ""
            for k, v in types.items():
                type_string += f" {k} {v.upper()},"
            type_string = type_string[:-1]

            async with aiosqlite.connect(self.filePath) as db:
                await db.execute(f"CREATE TABLE {name} ({type_string})")
                await db.commit()

        async def _insert_row(self, table_name: str, values: tuple):
            """
            Inserts the given row into the given table
            Args:
                table_name (str): Name of table to insert into
                values (tuple): values to insert into the given table.
                    amount and ordering must match the table columns

            Returns: None

            Raises:
                sqlite3.OperationalError: When the statement was malformed, most likely because
                  the length of the tuple wasn't equal to the number of columns
                ValueError: When the given table does not exist
            """
            if not await self._has_table(table_name):
                raise ValueError(f"Table {table_name} does not exist")

            value_string: str = ", ".join(values)

            async with aiosqlite.connect(self.filePath) as db:
                await db.execute(f"INSERT INTO '{table_name}' VALUES (?)", (value_string,))
                await db.commit()

        async def _select_rows(self, table_name: str, connector: str, condition: dict = None) -> list:
            """
            Return the rows from the specified table and filters them by the specified conditions.
                Supports 'AND' and 'OR'
            Args:
                table_name (str): name of table to select from
                connector (str): either 'AND' or 'OR'
                condition(dict): a dict of conditions to filter the result.
                    these will be connected via 'connector' and in the end
                        must be true for the given row
                            to be included in the result
            Returns: list[tuple]
                list of tuples, where each tuple represents the row,
                    and each element of the tuple represents the value of the column.
            """
            if condition is None:
                condition = {}
            if not await self._has_table(table_name):
                raise ValueError(f"Table {table_name} does not exist")

            connector = connector.upper()
            if connector not in ["AND", "OR"]:
                raise ValueError(f"Connector {connector} not supported")

            condition_string: str = ""
            for k, v in condition.items():
                condition_string += f" {k}='{v}' {connector}"
            if len(condition) > 0:
                condition_string = condition_string[1:-len(connector)]

            print(f"SELECT * FROM '{table_name}' WHERE {condition_string}")

            async with aiosqlite.connect(self.filePath) as db:
                cursor = await db.execute(
                    f"SELECT * FROM {table_name} WHERE ?", (condition_string,)
                )
                await db.commit()
                result = await cursor.fetchall()
                await cursor.close()
                return list(result)

        async def _update_row(self, table_name: str, connector: str, values: dict, condition=None):
            """
            Updates the rows of the given table with the given values
                filtering with the given conditions.
            Args:
                table_name (str): name of table to update
                connector (str): 'AND' or 'OR'
                values (dict): new value set. key is column name, value is new column value.
                condition (dict): the set of conditions to be fulfilled to update the column

            Returns: None
            Raises: ValueError
                If:
                1.: The table does not exist
                2.: No condition was given
                3.: the Connector was not 'AND' or 'OR'
            """
            if condition is None:
                condition = {}
            if not await self._has_table(table_name):
                raise ValueError(f"Table {table_name} does not exist")

            if len(condition) <= 0:
                raise ValueError("No conditions were given!")

            connector = connector.upper()
            if connector not in ["AND", "OR"]:
                raise ValueError("")

            condition_string: str = ""
            for k, v in condition.items():
                condition_string += f" {k}='{v}' {connector}"
            if len(condition_string) > 0:
                condition_string = condition_string[1:-len(connector)]

            value_string: str = ""
            for k, v in values.items():
                value_string += f" {k}='{v}',"

            value_string = value_string[1:-1]

            async with aiosqlite.connect(self.filePath) as db:
                print("update string = " + f"UPDATE '{table_name}' SET {value_string} WHERE {condition_string}")
                cursor = await db.execute(f"UPDATE '{table_name}' SET {value_string} WHERE ?", (condition_string,))
                await db.commit()
                await cursor.close()

        async def _delete_row(self, table_name: str, connector: str, condition=None):
            """
            deletes the rows from the specified table and filters them by the specified conditions.
                Supports 'AND' and 'OR'

            Args:
                table_name (str): name of table to delete from
                connector (str): either 'AND' or 'OR'
                condition (dict): a dict of conditions to filter the result.
                    these will be connected via 'connector'  and in the end
                    must be true for the given row to be deleted

            Returns: None

            Raises: ValueError
                1. should connector not be 'OR' or 'AND'
                2. When the given table does not exist
            """
            if condition is None:
                condition = {}
            if not await self._has_table(table_name):
                raise ValueError(f"Table {table_name} does not exist")

            if not len(condition) > 0:
                raise ValueError("No conditions were given!")

            connector = connector.upper()
            if connector not in ["AND", "OR"]:
                raise ValueError(f"Connector {connector} not supported")

            condition_string: str = ""
            for k, v in condition.items():
                condition_string += f"{k}='{v}' {connector} "
            condition_string = condition_string[:-(len(connector) + 1)]

            async with aiosqlite.connect(self.filePath) as db:
                await db.execute(f"DELETE FROM '{table_name}' WHERE ?", (condition_string,))
                await db.commit()

    async def get_fact(self, name: str, preferred_lang: str) -> str:
        """
        Return the fact for the given fact name and language.
        If the preferred_language doesnt exist, it returns the fact for the english language.
        If neither exist, it returns an empty string
        Args:
            name:
             str: name of the fact
            preferred_lang:
             str: preferred language

        Returns:
            str: fact for the given language, the english language or
                an empty string, if neither exist.

        """
        result = await self.__instance._select_rows(
            "mecha3-facts", "AND", {"lang": preferred_lang, "fact": name}
        )
        if len(result) <= 0:
            result = await self.__instance._select_rows(
                "mecha3-facts", "AND", {"lang": "en", "fact": name}
            )
        return result[0][2] if len(result) > 0 else ""
