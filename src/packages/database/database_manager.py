"""
database_manager.py - allows connections to SQL databases.
Provides postgreSQL connectivity for mechasqueak3.
Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.
Licensed under the BSD 3-Clause License.
See LICENSE.md
"""

import typing
import psycopg2
from loguru import logger
from psycopg2 import sql, pool

from src.config import CONFIG_MARKER
from src.config.datamodel import ConfigRoot


class DatabaseManager:
    """
    Database Manager class intended to be inherited by a parent class that requires database
    connectivity.  Currently, only PostgreSQL 9.5+ is supported.

    ODBC drivers are not required on Windows.

        Usage:
        >>> DatabaseManager(dbhost='DatabaseServer.org',
        ...                 dbport=5432,
        ...                 dbname='DatabaseName',
        ...                 dbuser='DatabaseUserName',
        ...                 dbpassword='UserPassword') # doctest: +SKIP

        All arguments are optional.  If omitted, config values will be pulled from config file.

        Instantiation of the DBM is not intended to be done per method, but rather once as a
        class property, and the DatabaseManage.query() method used to perform a query.

        Connections are managed by a SimpleConnectionPool, keeping a minimum of 5 and a maximum
        of 10 connections, able to dynamically open/close ports as needed.

        Performing A Query:
        .query() does not accept a direct string.  You must use a psycopg2 composed SQL (sql.SQL)
        object, with appropriate substitutions.

        DO NOT USE STRING CONCATENATION OR APPEND VALUES.  THIS IS BAD PRACTICE, AND AN INJECTION
        RISK!

        >>> query = sql.SQL(
        ... "SELECT FROM public.table WHERE table.name=%s AND table.lang=%s AND table.something=%s")

        >>> dbm.query(query, ('tuple','of','values'))# doctest: +SKIP

    """

    _config: typing.ClassVar[typing.Dict] = {}

    @classmethod
    @CONFIG_MARKER
    def rehash_handler(cls, data: ConfigRoot):
        """
        Apply new configuration data

        Args:
            data (typing.Dict): new configuration data to apply.

        """
        cls._config = data

    @classmethod
    @CONFIG_MARKER
    def validate_config(cls, data: typing.Dict):
        """
        Validate database portion of the configuration file

        Args:
            data(typing.Dict): configuration object
        """

        module_config = data["database"]

        # Require all values to be set
        for setting in module_config.values():
            if not setting:
                raise ValueError(f"[database]{setting} is required for instantiation but was empty")

        # Host
        if not isinstance(module_config["host"], str):
            raise ValueError("[database]host must be a string.")

        # Port
        if not isinstance(module_config["port"], int):
            raise ValueError("[database]port must be an integer.")

        # Database Name
        if not isinstance(module_config["dbname"], str):
            raise ValueError("[database]database name must be a string.")

        # Database Username
        if not isinstance(module_config["username"], str):
            raise ValueError("[database]database username must be a string.")

        # Database Password
        if not isinstance(module_config["password"], str):
            raise ValueError("[database]database password must be a string")

    def __init__(self, dbhost=None, dbport=None, dbname=None, dbuser=None, dbpassword=None):

        if not hasattr(self, "_initialized"):
            self._initialized = True

            # Utilize function arguments if they are provided,
            # otherwise retrieve from config file and use those values.
            self._dbhost = dbhost if dbhost is not None else self._config.database.host
            if not self._dbhost:
                raise AssertionError("_dbhost is not set")

            self._dbport = dbport if dbhost is not None else self._config.database.port
            if not self._dbport:
                raise AssertionError("_dbhost is not set")

            self._dbname = dbname if dbname is not None else self._config.database.dbname
            if not self._dbname:
                raise AssertionError("_dbhost is not set")

            self._dbuser = dbuser if dbuser is not None else self._config.database.username
            if not self._dbuser:
                raise AssertionError("_dbhost is not set")

            self._dbpass = (
                dbpassword if dbpassword is not None else self._config.database.password
            )
            if not self._dbpass:
                raise AssertionError("_dbhost is not set")

        # Create Database Connections Pool
        try:
            self._dbpool = psycopg2.pool.SimpleConnectionPool(
                5,
                10,
                host=self._dbhost,
                port=self._dbport,
                dbname=self._dbname,
                user=self._dbuser,
                password=self._dbpass,
            )

        except psycopg2.DatabaseError as error:
            logger.exception("Unable to connect to database!")
            raise error

    async def is_connected(self) -> bool:
        """
        Private method.  Verifies the isolation level as an alternative to
        an actual query to check if the connection is still alive and valid.
        """
        try:
            with self._dbpool.getconn() as connection:
                heartbeat = connection.isolation_level
                self._dbpool.putconn(connection)
        except psycopg2.OperationalError:
            logger.warning("Potential Connectivity issues with database!")
            return False

        return True

    async def query(
        self, query: sql.SQL, values: typing.Union[typing.Tuple, typing.Dict]
    ) -> typing.List:
        """
        Send a query to the connected database.  Pulls a connection from the pool and creates
        a cursor, executing the composed query with the values.
        Requires a composed SQL object (See psycopg2 docs)

        Args:
            query: composed SQL query object
            values: tuple or dict of values for query
        Returns:
            List of rows matching query.  May return an empty list if there are no matching rows.
        """
        # Verify composed SQL object
        if not isinstance(query, sql.SQL):
            raise TypeError("Expected composed SQL object for query.")

        # Verify value is tuple or dict.
        if not isinstance(values, (dict, tuple)):
            raise TypeError(f"Expected tuple or dict for query values.")

        # Pull a connection from the pool, and create a cursor from it.
        with self._dbpool.getconn() as connection:
            # If we could set these at connection time, we would,
            # but they must be set outside the pool.
            connection.autocommit = True
            connection.set_client_encoding("utf-8")
            # Create cursor, and execute the query.
            with connection.cursor() as cursor:
                if __debug__:
                    logger.debug("executing query {}", query)  # noinspection PyUnreachableCode
                cursor.execute(query, values)
                # Check if cursor.description is NONE - meaning no results returned.
                if cursor.description:
                    result = cursor.fetchall()
                else:
                    # Return a blank tuple if there are no results, since we are
                    # forcing this to a list.
                    result = ()

        # Release connection back to the pool.
        self._dbpool.putconn(connection)

        return list(result)
