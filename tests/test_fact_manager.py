"""
test_fact_manager.py


Tests for the logging module

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import datetime

import psycopg2
import pytest
from psycopg2 import sql

from src.packages.fact_manager.fact_manager import FactManager, Fact

pytestmark = pytest.mark.fact_manager


@pytest.fixture(scope='session')
def test_fm_fx(request) -> FactManager:
    """
    This fixture uses some dirty tricks to create a table, inject test data into it,
    and then tear it down after use.  This fixture REQUIRES a connection to a live database,
    with table creation and drop table permissions.

    You may wish to skip this test using pytest 'not fact_manager' if you do not have a database
    connection available.
    """
    test_table = "pytest_session_table"
    test_log = "pytest_session_log"

    test_table_creation = sql.SQL(f"CREATE TABLE {test_table} "
                                  f"(name VARCHAR NOT NULL, lang VARCHAR NOT NULL,"
                                  f" message VARCHAR NOT NULL, aliases TSVECTOR,"
                                  f" author VARCHAR, edited TIMESTAMP WITH TIME ZONE,"
                                  f" editedby VARCHAR, mfd BOOLEAN,"
                                  f" CONSTRAINT pytest_fact_pkey PRIMARY KEY (name, lang))")

    test_log_table_creation = sql.SQL(f"CREATE TABLE {test_log} "
                                      f"(id SERIAL, name VARCHAR NOT NULL,"
                                      f" lang VARCHAR NOT NULL,"
                                      f" author VARCHAR NOT NULL,"
                                      f" message VARCHAR NOT NULL,"
                                      f" old VARCHAR, new VARCHAR,"
                                      f" ts TIMESTAMP WITH TIME ZONE,"
                                      f" CONSTRAINT pytest_log_pkey PRIMARY KEY (id))")

    test_data = [f"INSERT INTO {test_table} (name, lang, message, author, editedby, edited) "
                 f"VALUES ('stats', 'en', 'Fuel Rats Statistics: https://t.fuelr.at/stats',"
                 f" 'CrunchyBaton955', 'CrunchyBaton955)', '{datetime.datetime(1970, 1, 1, 0, 0, 0)}')",
                 f"INSERT INTO {test_table} (name, lang, message, author, editedby, edited) "
                 f"VALUES ('test', 'en', 'This is a test fact.', 'Shatt', 'Shatt',"
                 f" '{datetime.datetime(1970, 1, 1, 0, 0, 0)}')",
                 f"INSERT INTO {test_table} (name, lang, message, author, editedby, edited) "
                 f"VALUES ('test', 'ru', 'This is a test fact. Чтобы зажечь "
                 f"маяк, зажмите клавижу Х и нажмите', 'Shatt', 'Shatt',"
                 f" '{datetime.datetime(1970, 1, 1, 0, 0, 0)}')"]

    pytest_fm = FactManager(fact_table=test_table, fact_log=test_log)

    # Let's add our test data:
    with pytest_fm._dbpool.getconn() as conn:
        conn.autocommit = True
        conn.set_client_encoding('utf-8')

        with conn.cursor() as cursor:
            cursor.execute(test_table_creation)
            cursor.execute(test_log_table_creation)
            # Add test data:
            for data in test_data:
                cursor.execute(data)

    def teardown():
        # Tear everything down
        with pytest_fm._dbpool.getconn() as conn:
            conn.autocommit = True
            conn.set_client_encoding('utf-8')

            with conn.cursor() as cursor:
                cursor.execute(f"DROP TABLE {test_table}")
                cursor.execute(f"DROP TABLE {test_log}")

    request.addfinalizer(teardown)
    return pytest_fm


def test_module_typeerror_fact_table(test_fm_fx):
    """
    Verify a TypeError is thrown, if assigning a non-str value to an optional property.
    """
    with pytest.raises(TypeError):
        testFM = FactManager(fact_table=["a list"])


def test_module_typeerror_log_table(test_fm_fx):
    """
    Verify a TypeError is thrown, if assigning a non-str value to an optional property.
    """
    with pytest.raises(TypeError):
        test_fm = FactManager(fact_log={"some": "dict"})


def test_module_prop_table(test_fm_fx):
    """
    Verify private properties are set when passed.
    """
    table_name = "some fact table"
    log_table_name = "some log table"

    test_fm = FactManager(table_name, log_table_name)

    assert test_fm._FACT_TABLE == table_name


def test_module_prop_log(test_fm_fx):
    """
    Verify private properties are set when passed.
    """
    table_name = "some fact table"
    log_table_name = "some log table"

    test_fm = FactManager(table_name, log_table_name)

    assert test_fm._FACT_LOG == log_table_name


@pytest.mark.asyncio
async def test_fm_add(test_fm_fx):
    """
    Verify the a fact added to the database is searchable and has all required properties.

    add_values = (fact.name, fact.lang, fact.message, None,
                              fact.author, fact.edited, fact.editedby, fact.mfd)
    """
    test_fact = Fact(name='test123', lang='en', message='This is a test fact for pytest',
                     editedby='Shatt', author='Shatt', mfd=False, edited=None, aliases=[])

    await test_fm_fx.add(test_fact)

    assert await test_fm_fx.exists("test123", "en")


@pytest.mark.asyncio
async def test_fm_add_incomplete(test_fm_fx):
    """
    Verify inserting an incomplete Fact raises TypeError.
    """
    test_fact = Fact('test123', 'en', 'This is an incomplete Fact',
                     None, 'Shatt', editedby=None)

    with pytest.raises(TypeError):
        await test_fm_fx.add(test_fact)


@pytest.mark.asyncio
async def test_fm_add_psycopg2_errors(test_fm_fx):
    """
    Verify an error is raised if a fact already exists.
    """
    test_fact = Fact(name='test123', lang='en', message='This is a test fact for pytest',
                     editedby='Shatt', author='Shatt', mfd=False, edited=None, aliases=[])

    # Intentionally add a fact with the same name:
    with pytest.raises(psycopg2.IntegrityError):
        await test_fm_fx.add(test_fact)


@pytest.mark.asyncio
async def test_fm_delete_mfd_check(test_fm_fx):
    """
    Verify deleting a fact marked mfd succeeds
    """

    test_fact = Fact(name='test127', lang='en', message='This is a test fact for pytest',
                     editedby='Shatt', author='Shatt', mfd=False, edited=None, aliases=[])
    await test_fm_fx.add(test_fact)
    assert await test_fm_fx.exists('test127', 'en')

    # Mark it for deletion
    await test_fm_fx.mfd('test127', 'en')

    # Attempt to delete it:
    await test_fm_fx.delete('test127', 'en')

    # ..and verify it is deleted.
    assert not await test_fm_fx.exists('test127', 'en')


@pytest.mark.asyncio
async def test_fm_delete_no_mfd_flag(test_fm_fx):
    """
    Verify deleting a fact NOT marked mfd fails, throwing a psycopg2.ProgrammingError
    """
    with pytest.raises(psycopg2.ProgrammingError):
        await test_fm_fx.delete('prep', 'en')


@pytest.mark.asyncio
async def test_mfdlist_returns_list(test_fm_fx):
    """
    mfd_list method must return a list.
    """
    assert isinstance(await test_fm_fx.mfd_list(), list)


@pytest.mark.asyncio
async def test_fm_destroy(test_fm_fx):
    """
    Verify _destroy function works properly.
    """
    await test_fm_fx._destroy('test', 'ru')


@pytest.mark.asyncio
async def test_edit_message_bad_fact(test_fm_fx):
    """
    Verify attempt to edit a fact that does not exist throws exception.
    """
    with pytest.raises(ValueError):
        await test_fm_fx.edit_message('notafact', 'nope', 'Shatt', 'This is not a fact')


@pytest.mark.asyncio
async def test_edit_message(test_fm_fx):
    """
    Test edit_message functionally works.
    """
    # async def edi(self, name: str, lang: str, editor: str, new_message: str):
    await test_fm_fx.edit_message('test', 'en', 'Shatt', 'This fact has been edited during testing.')

    result = await test_fm_fx.find('test', 'en')

    assert result.message == 'This fact has been edited during testing.'


@pytest.mark.asyncio
async def test_fact_exists(test_fm_fx):
    """
    Verify a fact looked up with the exists method returns true.
    """
    assert await test_fm_fx.exists('stats', 'en')


@pytest.mark.asyncio
async def test_fact_exists_no(test_fm_fx):
    """
    Verify a fact looked up with the exist method returns false if not found.
    """
    assert not await test_fm_fx.exists('asdf', 'asdfa')


@pytest.mark.asyncio
async def test_facthistory_return(test_fm_fx):
    """
    Verify fact history returns log entries.
    """
    # Add some log entries.
    await test_fm_fx.add_transaction('stats', 'en', 'Shatt', 'Added')
    await test_fm_fx.add_transaction('stats', 'en', 'Shatt', 'Deleted')
    await test_fm_fx.add_transaction('stats', 'en', 'Shatt', 'Added')
    await test_fm_fx.add_transaction('stats', 'en', 'Shatt', 'Marked for Delete')

    history = await test_fm_fx.fact_history('stats', 'en')
    assert history is not None


@pytest.mark.asyncio
async def test_facthistory_invalid_query(test_fm_fx):
    """
    Verify fact history raises no errors on an invalid fact lookup.
    """
    history = await test_fm_fx.fact_history('s205gw', 'sdjn3nw')


@pytest.mark.asyncio
async def test_fact_find_return(test_fm_fx):
    """
    Verify fact finder returns a complete fact object.
    """
    found_fact = await test_fm_fx.find('stats', 'en')

    assert found_fact.complete is True


@pytest.mark.asyncio
async def test_exist_exception_handling(test_fm_fx, monkeypatch):
    """
    Verify the error is caught if psycopg2.ProgrammingError is raised.
    """

    async def boomstick(*args, **kwargs):
        raise psycopg2.ProgrammingError("Raised by Pytest - Fire in the hole!")

    monkeypatch.setattr(test_fm_fx, "query", boomstick)

    with pytest.raises(psycopg2.ProgrammingError):
        result = await test_fm_fx.exists('fake', 'en')


@pytest.mark.asyncio
async def test_edit_exception_handling(test_fm_fx, monkeypatch):
    """
    Verify the error is caught if psycopg2.ProgrammingError is raised.
    """

    async def boomstick(*args, **kwargs):
        raise psycopg2.ProgrammingError("Raised by Pytest - Fire in the hole!")

    monkeypatch.setattr(test_fm_fx, "query", boomstick)

    with pytest.raises(psycopg2.ProgrammingError):
        result = await test_fm_fx.edit_message('test', 'en', 'Shatt',
                                               'This fact has been edited during testing.')


@pytest.mark.asyncio
async def test_facthistory_exception_handling(test_fm_fx, monkeypatch):
    """
    Verify the error is caught if psycopg2.ProgrammingError is raised.
    """

    async def boomstick(*args, **kwargs):
        raise psycopg2.ProgrammingError("Raised by Pytest - Fire in the hole!")

    monkeypatch.setattr(test_fm_fx, "query", boomstick)

    with pytest.raises(psycopg2.ProgrammingError):
        result = await test_fm_fx.fact_history('test', 'en')


@pytest.mark.asyncio
async def test_find_exception_handling(test_fm_fx, monkeypatch):
    """
    Verify the error is caught if psycopg2.ProgrammingError is raised.
    """

    async def boomstick(*args, **kwargs):
        raise psycopg2.ProgrammingError("Raised by Pytest - Fire in the hole!")

    monkeypatch.setattr(test_fm_fx, "query", boomstick)

    with pytest.raises(psycopg2.ProgrammingError):
        result = await test_fm_fx.find('test', 'en')


@pytest.mark.asyncio
async def test_log_exception_handling(test_fm_fx, monkeypatch):
    """
    Verify the error is caught if psycopg2.ProgrammingError is raised.
    """

    async def boomstick(*args, **kwargs):
        raise psycopg2.ProgrammingError("Raised by Pytest - Fire in the hole!")

    monkeypatch.setattr(test_fm_fx, "query", boomstick)

    with pytest.raises(psycopg2.ProgrammingError):
        result = await test_fm_fx.add_transaction('test', 'en', 'Shatt', 'Edited')


@pytest.mark.asyncio
async def test_mfd_handling(test_fm_fx, monkeypatch):
    """
    Verify the error is caught if psycopg2.ProgrammingError is raised.
    """

    async def boomstick(*args, **kwargs):
        raise psycopg2.ProgrammingError("Raised by Pytest - Fire in the hole!")

    monkeypatch.setattr(test_fm_fx, "query", boomstick)

    with pytest.raises(psycopg2.ProgrammingError):
        result = await test_fm_fx.mfd('test', 'en')


@pytest.mark.asyncio
async def test_mfdlist_handling(test_fm_fx, monkeypatch):
    """
    Verify the error is caught if psycopg2.ProgrammingError is raised.
    """

    async def boomstick(*args, **kwargs):
        raise psycopg2.ProgrammingError("Raised by Pytest - Fire in the hole!")

    monkeypatch.setattr(test_fm_fx, "query", boomstick)

    with pytest.raises(psycopg2.ProgrammingError):
        result = await test_fm_fx.mfd_list()
