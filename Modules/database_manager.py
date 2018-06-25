"""
database_manager.py - Manages access to the central database file

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import pyodbc
import config
import logging

log = logging.getLogger(f"mecha.{__name__}")


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# noinspection SqlNoDataSourceInspection
class DatabaseManager(metaclass=Singleton):

    def __init__(self):
        """
        Connects to the DB, sets up the connection, retrieves the cursor.
        Creates the default tables should they not exist.
        """
        # connect to PostgreSQL (PSQL) database
        __config: dict = config.config.get("database")
        connect_str = ("Driver={PostgreSQL UNICODE};"
                       f"Server={__config.get('server')};"
                       f"Port={__config.get('port')};"
                       f"Database={__config.get('database')};"
                       f"Uid={__config.get('username')};"
                       f"Pwd={__config.get('password')};"
                       "MaxVarcharSize=1024 * 1024 * 1024"
                       # Allow bigger VarcharSize to allow faster interaction
                       )
        self.connection: pyodbc.Connection = pyodbc.connect(connect_str, autocommit=True)
        self.connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        self.connection.setencoding(encoding='utf-8')
        self.connection.maxwrite = 1024 * 1024 * 1024  # Again, increase this for faster access
        self.cursor = self.connection.cursor()
        # Ensure all the default tables are defined
        self.cursor.execute("CREATE TABLE IF NOT EXISTS"
                            " mecha3_facts (name VARCHAR, lang VARCHAR, response VARCHAR);")

    async def _select_rows(self, table_name: str, connector: str, condition: dict = None,
                           skipdouble_dash_test: bool = False) -> list:
        """

        Args:
            table_name: name of the table to select from
            connector: Connector used to connect conditions. Must be suported by the DB
            condition: conditions, connected by "equals"
            skipdouble_dash_test: skip the crude SQLInjection test if it breaks your request,
                    implement your OWN CHECK!

        Returns: a list containing the rows returned

        """
        if await self._has_table(table_name):
            if not condition:
                condition = {}
            cond_str = ""
            for k, v in condition.items():
                cond_str += f"{k} = '{v}' {connector}"
            cond_str = cond_str[0:-len(connector) - 1]
            if ("--" in cond_str) and not skipdouble_dash_test:
                raise ValueError("Suspicion of SQL-Injection. Statement: SELECT * FROM {table_name}"
                                 f" WHERE {cond_str}. Aborting")
            return self.cursor.execute(f"SELECT * FROM {table_name} WHERE {cond_str};").fetchall()
        else:
            raise ValueError(f"Table {table_name} does not exists!")

    async def _has_table(self, name: str) -> bool:
        """
        checks whether the table exists.
        Unique to PSQL!

        Args:
            name: name of the table to check

        Returns: false if table does not exist, true otherwise

        """
        return self.cursor.execute(("SELECT EXISTS ( "
                                    "SELECT 1 FROM pg_tables WHERE tablename = '{name}')"
                                    " as result;").format(name=name)).fetchone()[0] != '0'

    async def _create_table(self, name: str, types: dict) -> None:
        """
            Creates the table with the given name and datatypes.
            All datatypes must be SQL-compliant.
        Args:
            name: name of table to create
            types: ict of column name and datatype

        Returns: None
        Raises: ValueError should table already exist
        """

        if not await self._has_table(name):
            type_str = ""
            for k, v in types.items():
                type_str += f"{k} {v},"
            type_str = type_str[:-1]
            self.cursor.execute(f"CREATE TABLE {name} ({type_str}) ;")
            self.connection.commit()
            return
        raise ValueError(f"Table {name} already exists!")

    async def _drop_table(self, name: str) -> None:
        """

        Args:
            name: name of table to drop

        Returns: None

        """
        if await self._has_table(name):
            sql_string = "DROP TABLE {name};".format(name=name)
            self.cursor.execute(sql_string)
            self.connection.commit()
            return
        raise ValueError(f"Table {name} does not exist!")

    async def _insert_row(self, table_name: str, values: tuple):
        """

        Args:
            table_name: name of table to insert value into
            values: tuple with values matching the rows to insert into

        Returns: None

        """
        if await self._has_table(table_name):
            sql_string = "INSERT INTO {table_name} VALUES (?);".format(table_name=table_name)
            val_str = ", ".join(values)
            self.cursor.execute(sql_string, (val_str,))
        else:
            raise ValueError(f"Table {table_name} does not exist")

    async def _update_row(self, table_name: str, connector: str, values: dict, condition=None,
                          skipdouble_dash_test=False):
        """

        Args:
            table_name: name of table to update
            connector: Connector used to connect conditions. Must be suported by the DB
            values: tuple with values matching the rows to insert into
            condition: conditions, connected by "equals"
            skipdouble_dash_test: skip the crude SQLInjection test if it breaks your request,
                    implement your OWN CHECK!

        Returns:

        """
        if await self._has_table(table_name):
            val_str = ""
            for k, v in values.items():
                val_str += f"{k} = '{v}',"
            val_str = val_str[:-1]
            cond_str = ""
            for k, v in condition.items():
                cond_str += f"{k} = '{v}' {connector}"
            cond_str = cond_str[0:-len(connector) - 1]
            if ("--" in cond_str or "--" in val_str) and not skipdouble_dash_test:
                raise ValueError(f"Suspicion of SQL-Injection.Statement: UPDATE {table_name} "
                                 f"SET {val_str} WHERE {cond_str}. Aborting")
            self.cursor.execute(f"UPDATE {table_name} SET {val_str} WHERE {cond_str};")
        else:
            raise ValueError(f"Table {table_name} does not exists!")

    async def _delete_row(self, table_name: str, connector: str, condition=None,
                          skipdouble_dash_test: bool = False):
        """

        Args:
            table_name: name of table to delete row form
            connector: Connector used to connect conditions. Must be suported by the DB
            condition: onditions, connected by "equals"
            skipdouble_dash_test: skip the crude SQLInjection test if it breaks your request,
                    implement your OWN CHECK!

        Returns:

        """
        if await self._has_table(table_name):
            cond_str = ""
            for k, v in condition.items():
                cond_str += f"{k} = '{v}' {connector}"
            cond_str = cond_str[0:-len(connector) - 1]
            if ("--" in cond_str) and not skipdouble_dash_test:
                raise ValueError(f"Suspicion of SQL-Injection. Statement: DELETE FROM {table_name}"
                                 f" WHERE {cond_str}. Aborting")
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {cond_str}")
