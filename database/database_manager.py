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
                 dbPort=None,
                 dbName=None,
                 dbUser=None,
                 dbPassword=None
                 ):

        if not hasattr(self, "_initialized"):
            self._initialized = True

            self._dbhost = config['database'].get('host')
            assert self._dbhost

            self._dbport = config['database'].get('port')
            assert self._dbport

            self._dbname = config['database'].get('dbname')
            assert self._dbname

            self._dbuser = config['database'].get('username')
            assert self._dbuser

            self._dbpass = config['database'].get('password')
            assert self._dbpass

        # Create Database Connections Pool
        try:
            self._dbpool = psycopg2.pool.SimpleConnectionPool(5, 10, host=self._dbhost, port=self._dbport,
                                                              dbname=self._dbname, user=self._dbuser,
                                                              password=self._dbpass)

            if self._dbpool:
                log.info("SQL Database Connected.")
        except (Exception, psycopg2.DatabaseError) as error:
            log.warning("Error connecting to SQL database.", error)

    async def query(self, query, values: tuple) -> list:
        with self._dbpool.getconn() as connection:
            connection.autocommit = True
            connection.set_client_encoding('utf-8')
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchall()

        self._dbpool.putconn(connection)

        return list(result)

