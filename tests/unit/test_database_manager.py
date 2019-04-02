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
from psycopg2 import extensions, sql

pytestmark = [pytest.mark.unit, pytest.mark.database_manager]


def test_init_values(test_dbm_fx):
    """
    Test and verify all values required for instantiation are not None.
    """
    assert test_dbm_fx._initialized
    assert test_dbm_fx._dbhost
    assert test_dbm_fx._dbpass
    assert test_dbm_fx._dbname
    assert test_dbm_fx._dbport
    assert test_dbm_fx._dbuser


def test_db_connection(test_dbm_pool_fx):
    """
    Pull a connection from the pool, and verify the status is able to receive a query.
    """
    with test_dbm_pool_fx.getconn() as connection:
        assert connection.status == psycopg2.extensions.STATUS_READY


def test_db_connection_close(test_dbm_pool_fx):
    """
    Assert that putting a connection back into the pool raises no error.
    """
    conn = test_dbm_pool_fx.getconn()
    test_dbm_pool_fx.putconn(conn, True)


def test_db_connection_autocommit(test_dbm_pool_fx):
    """
    Verify autocommit is valid when set.
    """
    with test_dbm_pool_fx.getconn() as conn:
        conn.autocommit = True
        assert conn.autocommit


def test_db_connection_client_encoding(test_dbm_pool_fx):
    """
    Verify client encoding is valid when set.
    """
    with test_dbm_pool_fx.getconn() as conn:
        conn.set_client_encoding('utf-8')
        assert conn.encoding == 'UTF8'


@pytest.mark.asyncio
async def test_query_sql_error(test_dbm_fx):
    """
    Verify a TypeError is raised if sending a string to query.
    """
    # Below statement is incorrect intentionally.
    with pytest.raises(TypeError) as error:
        result = await test_dbm_fx.query("This is a test", (15, 122))


@pytest.mark.asyncio
async def test_query_value_error(test_dbm_fx):
    """
    Verify a TypeError is raised if sending a non-tuple as query value.
    """
    # Below statement is incorrect intentionally.
    with pytest.raises(TypeError) as error:
        result = await test_dbm_fx.query(sql.SQL("SELECT * FROM {}", ["Happy", [1, 3, 4]]))


def test_db_query_pool(test_dbm_pool_fx):
    """
    Query the database using a connection pool.
    """
    with test_dbm_pool_fx.getconn().cursor() as cursor:
        cursor.execute("SELECT name, lang ,message from fact WHERE name = 'test' AND lang='en'")
        result = cursor.fetchall()

        assert result == [('test', 'en', 'This is a test fact.')]


@pytest.mark.asyncio
async def test_db_query_direct(test_dbm_fx):
    """
    Query the database using the query function directly.
    """
    assert await test_dbm_fx.query(sql.SQL("SELECT name, lang, message "
                                        "from fact WHERE name=%s AND lang=%s"),
                                   ('test', 'en')) == [('test', 'en', 'This is a test fact.')]
