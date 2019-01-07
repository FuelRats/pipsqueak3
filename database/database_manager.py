"""
database_manager.py - allows connections to SQL databases.
Provides postgreSQL connectivity for mechasqueak3.
Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.
Licensed under the BSD 3-Clause License.
See LICENSE.md
"""
from config import config
from psycopg2 import sql, pool
from typing import Union, Tuple, List, Dict
import logging
import psycopg2

log = logging.getLogger(f"mecha.{__name__}")


class DatabaseManager(object):
    """
    Database Manager class intended to be inherited by a parent class that requires database
    connectivity.  Currently, only PostgreSQL 9.5+ is supported.

    ODBC drivers are not required on Windows.

        Usage:
        >>> DatabaseManager(dbhost='DatabaseServer.org',
        ...                 dport=5432,
        ...                 dbname='DatabaseName',
        ...                 dbuser='DatabaseUserName',
        ...                 dbpassword='UserPassword')

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

        >>> query = sql.SQL("SELECT FROM public.table WHERE" \
        ...                 "table.name=%s AND table.lang=%s AND table.something=%s")
        ... DatabaseManager.query(query, ('tuple','of','values'))

    """

    def __init__(self,
                 dbhost=None,
                 dbport=None,
                 dbname=None,
                 dbuser=None,
                 dbpassword=None
                 ):

        if not hasattr(self, "_initialized"):
            self._initialized = True

            # Utilize function arguments if they are provided,
            # otherwise retrieve from config file and use those values.
            self._dbhost = dbhost if dbhost is not None else config['database'].get('host')
            assert self._dbhost

            self._dbport = dbport if dbhost is not None else config['database'].get('port')
            assert self._dbport

            self._dbname = dbname if dbname is not None else config['database'].get('dbname')
            assert self._dbname

            self._dbuser = dbuser if dbuser is not None else config['database'].get('username')
            assert self._dbuser

            self._dbpass = dbpassword if dbpassword is not None else \
                config['database'].get('password')
            assert self._dbpass

        # Create Database Connections Pool
        try:
            self._dbpool = psycopg2.pool.SimpleConnectionPool(5, 10, host=self._dbhost,
                                                              port=self._dbport,
                                                              dbname=self._dbname,
                                                              user=self._dbuser,
                                                              password=self._dbpass)

        except psycopg2.DatabaseError as error:
            log.exception("Unable to connect to database!")
            raise error

    async def query(self, query: sql.SQL, values: Union[Tuple, Dict]) -> List:
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
        if not isinstance(values, (Dict, Tuple)):
            raise TypeError(f"Expected tuple or dict for query values.")

        # Pull a connection from the pool, and create a cursor from it.
        with self._dbpool.getconn() as connection:
            # If we could set these at connection time, we would,
            # but they must be set outside the pool.
            connection.autocommit = True
            connection.set_client_encoding('utf-8')
            # Create cursor, and execute the query.
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                # Check if cursor.description is NONE - meaning no results returned.
                if cursor.description:
                    result = cursor.fetchall()
                else:
                    # Return a blank tuple if there are no results, since we are
                    # forcing this to a list.
                    result = tuple()

        # Release connection back to the pool.
        self._dbpool.putconn(connection)

        return list(result)
