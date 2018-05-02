"""
database_manager.py - Manages access to the central database file

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import sqlite3


class DataBaseManager:
    instance = None

    def __init__(self, file_name: str = "mecha3.db"):
        """
        Creates the master instance of the nested singleton class
        """
        if not self.instance:
            self.instance = self.__DatabaseManager(file_name)

#    def __getattr__(self, item):
#        """
#        Redirects the getattr calls to the singleton class
#        """
#        return getattr(self.instance, item)

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
            self.connection = sqlite3.connect(self.filePath)
            if self._has_table("mecha3-facts"):
                self._create_table("mecha3-facts", {"fact": "STRING", "lang": "STRING", "text": "STRING"})

        def _has_table(self, name: str):
            """

            Args:
                name (str): name of the table to check

            Returns: True when table exists, false otherwise

            """
            return len(self.connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
                .fetchall()) >= 1

        def _create_table(self, name: str, types: dict):
            """
            Creates the table with the given name and columns
            Args:
                name (str): name of the table to create
                types (dict): dict of columns, key denotes the name, value the type.
                    type must be a valid SQL type

            Returns: None
            """
            if self._has_table(name):
                raise ValueError(f"Table {name} already exists")
            type_string: str = ""
            for k, v in types.items():
                type_string += f" {k} {v.upper()},"
            type_string = type_string[:-1]
            self.connection.execute("CREATE TABLE {name} ({t_string})".format(name=name,
                                                                              t_string=type_string))

        def _insert_row(self, table_name: str, values: tuple):
            """
            Inserts the given row into the given table
            Args:
                table_name (str): Name of table to insert into
                values (tuple): values to insert into the given table.
                    amount and ordering must match the table columns

            Returns: None

            Raises:
                sqlite3.OperationalError: When the statement was malformed, most likely because
                 #  the length of the tuple wasn't equal to the number of columns
                ValueError: When the given table does not exist
            """
            if not self._has_table(table_name):
                raise ValueError(f"Table {table_name} does not exist")

            value_string: str = ""
            for k in values:
                value_string += f"{k},"
            value_string = value_string[:-1]

            self.connection.execute("INSERT INTO '{tablename}' VALUES (?)".format(tablename=table_name),
                                    (value_string,))

        def _select_rows(self, table_name: str, connector: str, condition=None) -> list:
            """
            Return the rows from the specified table and filters them by the specified conditions.
                Supports 'AND' and 'OR'
            Args:
                table_name (str): name of table to select from
                connector (str): either 'AND' or 'OR'
                condition(dict): a dict of conditions to filter the result.
                    these will be connected via 'connector' and in the end must be true for the given row
                        to be included in the result
            Returns: list[tuple]
                list of tuples, where each tuple represents the row,
                    and each element of the tuple represents the value of the column.
            """
            if condition is None:
                condition = {}
            if not self._has_table(table_name):
                raise ValueError(f"Table {table_name} does not exist")

            connector = connector.upper()
            if connector not in ["AND", "OR"]:
                raise ValueError(f"Connector {connector} not supported")

            condition_string: str = ""
            for k, v in condition.items():
                condition_string += f" {k}='{v}' {connector}"
            if len(condition) > 0:
                condition_string = condition_string[:-len(connector)]
                condition_string = f" WHERE {condition_string}"

            return self.connection.execute("SELECT * FROM '{tablename}' {cond_str}".
                                           format(tablename=table_name, cond_str=condition_string)).fetchall()

        def _update_row(self, table_name: str, connector: str, values: dict, condition=None):
            """
            Updates the rows of the given table with the given values filtering with the given conditions.
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
            if not self._has_table(table_name):
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
                condition_string = condition_string[:-len(connector)]

            value_string: str = ""
            for k, v in values.items():
                value_string += f" {k}='{v}',"

            value_string = value_string[:-1]

            self.connection.execute(f"UPDATE '{table_name}' SET {value_string} WHERE {condition_string}")

        def _delete_row(self, table_name: str, connector: str, condition=None):
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
            if not self._has_table(table_name):
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

            self.connection.execute(f"DELETE FROM '{table_name}' WHERE {condition_string}")

    def get_fact(self, name: str, preferred_lang: str):
        """
        Return the fact for the given fact name and language.
        If the preferred_language doesnt exist, it returns the fact for the english language.
        If neither exist, it returns an empty string
        Args:
            name(str): name of the fact
            preferred_lang (str): preferred language

        Returns(str): fact for the given language, the english language or an empty string, if neither exist.

        """
        result = self.instance._select_rows("mecha3-facts", "AND", {"lang": preferred_lang, "fact":name})
        if len(result) <= 0:
            result = self.instance._select_rows("mecha3-facts", "AND", {"lang": "en", "fact":name})
        return result[0][2] if len(result) > 0 else ""
