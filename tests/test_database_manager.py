"""
test_database_manager.py - tests for the DatabaseManager package.

A database configuration and connection is required for these tests.
No data will be written to or deleted from the database.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
import pytest
import psycopg2
from database import DatabaseManager
from psycopg2 import extensions, pool, sql

pytestmark = pytest.mark.database_manager


def test_dbm_singleton():
    """
    Verify that DBM is indeed a singleton and not spawning a new instance.
    """
    class Pirate(DatabaseManager):
        ...

    ship_crew = Pirate()
    hating_sharks = Pirate()

    assert ship_crew is hating_sharks


def test_init_values(test_dbm):
    """
    Test and verify all values required for instantiation are not None.
    """
    assert test_dbm._initialized
    assert test_dbm._dbhost
    assert test_dbm._dbpass
    assert test_dbm._dbname
    assert test_dbm._dbport
    assert test_dbm._dbuser


def test_db_connection(test_dbm_pool):
    """
    Pull a connection from the pool, and verify the status is able to receive a query.
    """
    with test_dbm_pool.getconn() as connection:
        assert connection.status == psycopg2.extensions.STATUS_READY


def test_db_connection_close(test_dbm_pool):
    """
    Assert that putting a connection back into the pool raises no error.
    """
    conn = test_dbm_pool.getconn()
    test_dbm_pool.putconn(conn, True)


def test_db_connection_autocommit(test_dbm_pool):
    """
    Verify autocommit is valid when set.
    """
    with test_dbm_pool.getconn() as conn:
        conn.autocommit = True
        assert conn.autocommit


def test_db_connection_client_encoding(test_dbm_pool):
    """
    Verify client encoding is valid when set.
    """
    with test_dbm_pool.getconn() as conn:
        conn.set_client_encoding('utf-8')
        assert conn.encoding == 'UTF8'


@pytest.mark.asyncio
async def test_query_sql_error(test_dbm):
    """
    Verify a TypeError is raised if sending a string to query.
    """
    # Below statement is incorrect intentionally.
    with pytest.raises(TypeError) as error:
        result = await test_dbm.query("This is a test", (15, 122))


@pytest.mark.asyncio
async def test_query_value_error(test_dbm):
    """
    Verify a TypeError is raised if sending a non-tuple as query value.
    """
    # Below statement is incorrect intentionally.
    with pytest.raises(TypeError) as error:
        result = await test_dbm.query(sql.SQL("SELECT * FROM {}", ["Happy", [1, 3, 4]]))


def test_db_query_pool(test_dbm_pool):
    """
    Query the database using a connection pool.
    """
    with test_dbm_pool.getconn().cursor() as cursor:
        cursor.execute("SELECT name, lang ,message from fact WHERE name = 'test' AND lang='en'")
        result = cursor.fetchall()

        assert result == [('test', 'en', 'This is a test fact.')]


@pytest.mark.asyncio
async def test_db_query_direct(test_dbm):
    """
    Query the database using the query function directly.
    """
    assert await test_dbm.query(sql.SQL("SELECT name, lang, message "
                                        "from fact WHERE name=%s AND lang=%s"),
                                ('test', 'en')) == [('test', 'en', 'This is a test fact.')]
