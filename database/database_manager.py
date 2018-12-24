"""
database_manager.py - Debug and diagnostics commands
Provides postgreSQL connectivity for mechasqueak3.
Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.
Licensed under the BSD 3-Clause License.
See LICENSE.md
"""
from config import config
from psycopg2 import sql, pool
from utils.ratlib import Singleton
import logging
import psycopg2

log = logging.getLogger(f"mecha.{__name__}")


class DatabaseManager(Singleton, object):

    def __init__(self,
                 dbhost=None,
                 dbport=None,
                 dbname=None,
                 dbuser=None,
                 dbpassword=None
                 ):

        if not hasattr(self, "_initialized"):
            self._initialized = True

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

            if self._dbpool:
                log.info("SQL Database Connected.")
        except (Exception, psycopg2.DatabaseError) as error:
            log.warning("Error connecting to SQL database.", error)

    async def query(self, query: sql.SQL, values: tuple) -> list:
        """
        Send a query to the connected database.  Pulls a connection from the pool and creates
        a cursor, executing the composed query with the values.
        Requires a composed SQL object (See psycopg2 docs)
        Args:
            query: composed SQL query object
            values: tuple of values for query
        Returns:
            List of rows matching query.  May return an empty list if there are no matching rows.
        """
        # Verify composed SQL object
        if not isinstance(query, sql.SQL):
            raise TypeError("Expected composed SQL object for query.")

        # Verify value is tuple
        if not isinstance(values, tuple):
            raise TypeError("Expected tuples for query values.")

        # Pull a connection from the pool, and create a cursor from it.
        with self._dbpool.getconn() as connection:
            # If we could set these at connection time, we would,
            # but they must be set outside the pool.
            connection.autocommit = True
            connection.set_client_encoding('utf-8')
            # Create cursor, and execute the query.
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchall()

        # Release connection back to the pool.
        self._dbpool.putconn(connection)

        return list(result)
