"""
database_manager.py - Manages access to the central database file

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import pyodbc
from config import config
import logging
from utils.ratlib import Singleton
from abc import abstractmethod, ABC
from typing import Dict, List, Tuple, Union, Optional, Any
import datetime

log = logging.getLogger(f"mecha.{__name__}")


class DBMApi(ABC):
    @abstractmethod
    async def select_rows(self, table_name: str, connector: str, condition: Dict[str, str] = None,
                          skip_double_dash_test: bool = False) -> Optional[List[Any]]:
        """

        Args:
            table_name: name of the table to select from
            connector: Connector used to connect conditions. Must be supported by the DB
            condition: conditions, connected by "equals"
            skip_double_dash_test: skip the crude SQLInjection test if it breaks your request,
                    implement your OWN CHECK!

        Returns: a list containing the rows returned

        """

    @abstractmethod
    async def has_table(self, name: str) -> bool:
        """
        checks whether the table exists.
        Unique to PSQL!

        Args:
            name: name of the table to check

        Returns: false if table does not exist, true if it exists

        """

    @abstractmethod
    async def create_table(self, name: str, types: Dict[str, str]) -> None:
        """
        Creates the table with the given name and datatypes.
        All datatypes must be SQL-compliant.

        Args:
            name: name of table to create
            types: dict of column name and datatype

        Returns: None
        Raises: ValueError should table already exist
        """

    @abstractmethod
    async def drop_table(self, name: str) -> None:
        """

        Args:
            name: name of table to drop

        Returns: None

        """

    @abstractmethod
    async def insert_row(self, table_name: str,
                         values: Dict[str, Union[str, datetime.datetime]],
                         constraint_column_name: Tuple[str],
                         no_conflict_resolution: bool = False,
                         skip_double_dash_test: bool = False) -> None:
        """

        Args:
            constraint_column_name: names of the unique columns.
                These MUST be set as unique at table-creation
            no_conflict_resolution: If there are no unique columns in your table, set this to True
            table_name: name of table to insert value into
            values: tuple with values matching the rows to insert into
            skip_double_dash_test: skip the crude SQLInjection test if it breaks your request,
                    implement your OWN CHECK!

        Returns: None

        """

    @abstractmethod
    async def update_row(self, table_name: str, connector: str,
                         values: Dict[str, Union[str, datetime.datetime]],
                         condition: Dict[str, str] = None,
                         skip_double_dash_test=False) -> None:
        """

         Args:
             table_name: name of table to update
             connector: Connector used to connect conditions. Must be suported by the DB
             values: tuple with values matching the rows to insert into
             condition: conditions, connected by "equals"
             skip_double_dash_test: skip the crude SQLInjection test if it breaks your request,
                     implement your OWN CHECK!

         Returns: None

         """

    @abstractmethod
    async def delete_row(self, table_name: str, connector: str, condition: Dict[str, str] = None,
                         skip_double_dash_test: bool = False) -> None:
        """

        Args:
            table_name: name of table to delete row form
            connector: Connector used to connect conditions. Must be suported by the DB
            condition: conditions, connected by "equals"
            skip_double_dash_test: skip the crude SQLInjection test if it breaks your request,
                    implement your OWN CHECK!

        Returns: None

        """


# noinspection SqlNoDataSourceInspection
class DatabaseManager(DBMApi, Singleton):
    _enabled = True

    # for testing only, as a makeshift "session" scope
    marker = None

    cursor = None

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(f"{type(value)} is not a valid type for setting a bool!")
        if value == self._enabled:
            # no need to change it if no change is required
            return
        if value:
            try:
                self.init_connection()
                self._enabled = True
            except pyodbc.Error as ex:
                log.error(f"Connection reinitialization failed! {ex}")
                raise
        else:
            self.connection.close()
            self._enabled = False

    def _execute(self, *args, **kwargs):
        if not self.enabled:
            log.warning("Tried to execute a DB call with the DB access being disabled.")
            raise RuntimeError("Check if the DB-module is enabled before executing code!"
                               " Currently it is NOT!")
        for retry in range(3):
            try:
                return self.cursor.execute(*args, **kwargs)
            except pyodbc.ProgrammingError as ex:
                self.last_error = ex
                if str(ex) == "The cursor's connection has been closed.":
                    self.init_connection()
                    continue
                else:
                    raise
            except pyodbc.Error as ex:
                self.last_error = ex
                if "the connection lost" in str(ex):
                    self.init_connection()
                    continue
                else:
                    raise
        self.enabled = False
        # raise self.last_error
        # would raise the above catched exceptions after failing three times

    # noinspection PyAttributeOutsideInit
    def init_connection(self):
        # connect to PostgreSQL (PSQL) database
        config_: Dict = config["database"]
        connect_str = None
        if config_["method"].lower() == "server":
            config_ = config_[config_["method"].lower()]
            connect_str = ("Driver={PostgreSQL UNICODE};"
                           f"Server={config_['server']};"
                           f"Port={config_['port']};"
                           f"Database={config_['database']};"
                           f"Uid={config_['username']};"
                           f"Pwd={config_['password']};"
                           "MaxVarcharSize=1024 * 1024 * 1024"
                           # Allow bigger VarcharSize to allow faster interaction
                           )
        else:
            config_ = config_[config_["method"].lower()]
            connect_str = (f"DSN={config_['dsn']};"
                           f"Uid={config_['username']};"
                           f"Pwd={config_['password']};"
                           "MaxVarcharSize=1024 * 1024 * 1024"
                           # Allow bigger VarcharSize to allow faster interaction
                           )
        self.connection: pyodbc.Connection = pyodbc.connect(connect_str, autocommit=True)
        # configure the connection
        self.connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        self.connection.setencoding(encoding='utf-8')
        self.connection.maxwrite = 1024 * 1024 * 1024  # Again, increase this for faster access
        # and create a cursor
        self.cursor = self.connection.cursor()
        self._enabled = True
        # Ensure all the default tables are defined
        self._execute("CREATE TABLE IF NOT EXISTS fact ("
                      "name VARCHAR NOT NULL,"
                      "lang VARCHAR NOT NULL,"
                      "message VARCHAR NOT NULL,"
                      "author VARCHAR, "
                      "PRIMARY KEY (name, lang) "
                      #  "UNIQUE (name, lang)"
                      ");"
                      )

        self._execute("CREATE TABLE IF NOT EXISTS fact_timestamps ("
                      "id SERIAL PRIMARY KEY,"
                      "name VARCHAR NOT NULL,"
                      "lang VARCHAR NOT NULL,"
                      "message VARCHAR NOT NULL,"
                      "author VARCHAR NOT NULL,"
                      "date_changed TIMESTAMP WITH TIME ZONE NOT NULL"
                      ");"
                      )

    def __init__(self):

        """
        Connects to the DB, sets up the connection, retrieves the cursor.
        Creates the default tables should they not exist.
        """

        # if we are not supposed to connect on start-up, we just sit tight and do nothing
        if not self.enabled:
            return
        # we init the connection, as we are supposed to do
        try:
            self.init_connection()
        except pyodbc.Error:
            # something went terribly wrong and excrements hit the ventilation device
            # using internal here to skip disconnection part as it might (and probably would) call
            # stuff on a NoneType
            self._enabled = False
            return

    async def select_rows(self, table_name: str, connector: str, condition: Dict[str, str] = None,
                          skip_double_dash_test: bool = False) -> List or None:

        # if we don't have that table, somebody didn't do their homework, so we just raise them.
        if await self.has_table(table_name):
            if not condition:
                condition = {}
            # we need the conditions written out as a string
            cond_str = f" {connector} ".join(f"{key} = '{value}'"
                                             for key, value in condition.items())
            # this is just a crude check trying to prevent SQL-Injection by disallowing comments
            if ("--" in cond_str) and not skip_double_dash_test:
                raise ValueError("Suspicion of SQL-Injection. Statement: SELECT * FROM {table_name}"
                                 f" WHERE {cond_str}. Aborting")
            # throw out the result of the query
            return self._execute(f"SELECT * FROM {table_name} WHERE {cond_str};").fetchall()
        else:
            # let's raise them to be responsible adults
            raise ValueError(f"Table {table_name} does not exists!")

    async def has_table(self, name: str) -> bool:

        # query whether that table exists in the index, than checking if that value isn't false
        # the result gets returned
        return self._execute(("SELECT EXISTS ( "
                              "SELECT 1 FROM pg_tables WHERE tablename = '{name}')"
                              " as result;").format(name=name)).fetchone()[0] != '0'

    async def create_table(self, name: str, types: Dict[str, str]) -> None:

        # You didn't do your homework AGAIN‽ let me raise you again....
        if not await self.has_table(name):
            # even the column definitions have to be in string form. its SQL after all
            type_str = ", ".join(f"{k} {v}" for k, v in types.items())
            # nicely asking the odbc-driver to create it for us
            self._execute(f"CREATE TABLE {name} ({type_str}) ;")
            #  and I'm outta here
            return
        # let's hope we don't have to raise him again
        raise ValueError(f"Table {name} already exists!")

    async def drop_table(self, name: str) -> None:
        """

        Args:
            name: name of table to drop

        Returns: None

        """
        # can't bin what isn't there
        if await self.has_table(name):
            # preparing the nuke
            sql_string = "DROP TABLE {name};".format(name=name)
            # and BOOM goes the nuke
            self._execute(sql_string)
            # lets vacate this irradiated area
            return
        # please, kid, do your homework
        raise ValueError(f"Table {name} does not exist!")

    async def insert_row(self, table_name: str, values: Dict[str, Union[str, datetime.datetime]],
                         constraint_column_name: tuple,
                         no_conflict_resolution: bool = False,
                         skip_double_dash_test: bool = False) -> None:

        if await self.has_table(table_name):
            val_str = col_str = val_col_str = ""
            for k, v in values.items():
                val_str += f"'{v}', "
                col_str += f"{k}, "
                val_col_str += f"{k} = '{v}', "

            val_col_str = val_col_str[:-2]
            val_str = val_str[:-2]
            col_str = col_str[:-2]

            # print(f"val_str = {val_str}\ncol_str = {col_str}\nval_col_str = {val_col_str}")

            constraint_str = ", ".join(constraint_column_name)
            if '--' in val_str and not skip_double_dash_test:
                raise ValueError(f"Suspicion of SQL-Injection. "
                                 f"Statement: INSERT INTO {table_name} VALUES ({val_str})")
            sql_string = f"INSERT INTO {table_name} ({col_str}) VALUES ({val_str})"
            if not no_conflict_resolution:
                sql_string += (f"ON CONFLICT ({constraint_str}) DO "
                               f"UPDATE SET {val_col_str};")

            self._execute(sql_string)
        else:
            raise ValueError(f"Table {table_name} does not exist")

    async def update_row(self, table_name: str,
                         connector: str,
                         values: Dict[str, Union[str, datetime.datetime]],
                         condition=None,
                         skip_double_dash_test=False) -> None:

        if await self.has_table(table_name):
            val_str = ", ".join(f"{k} = '{v}'" for k, v in values.items())
            cond_str = f" {connector} ".join(f"{key} = '{value}'"
                                             for key, value in condition.items())

            if ("--" in cond_str or "--" in val_str) and not skip_double_dash_test:
                raise ValueError(f"Suspicion of SQL-Injection.Statement: UPDATE {table_name} "
                                 f"SET {val_str} WHERE {cond_str}. Aborting")
            self._execute(f"UPDATE {table_name} SET {val_str} WHERE {cond_str};")
        else:
            raise ValueError(f"Table {table_name} does not exists!")

    async def delete_row(self, table_name: str, connector: str, condition: Dict[str, str] = None,
                         skip_double_dash_test: bool = False) -> None:

        if await self.has_table(table_name):
            cond_str = f" {connector} ".join(f"{key} = '{value}'"
                                             for key, value in condition.items())
            if ("--" in cond_str) and not skip_double_dash_test:
                raise ValueError(f"Suspicion of SQL-Injection. Statement: DELETE FROM {table_name}"
                                 f" WHERE {cond_str}. Aborting")
            self._execute(f"DELETE FROM {table_name} WHERE {cond_str}")
