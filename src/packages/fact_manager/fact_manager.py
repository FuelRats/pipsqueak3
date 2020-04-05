"""
fact_manager.py - Fact Management

Provides a context manager for manipulating, retrieving, and storing facts.
This class requires database.DatabaseManager and Modules.fact.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import datetime
import psycopg2
from psycopg2 import sql
from loguru import logger
from .fact import Fact
from ..database import DatabaseManager


class FactManager(DatabaseManager):
    """
    Fact Manager class inherits DatabaseManager to provide methods for interfacing with Fact objects
    stored in a fact table.

    Args:
        fact_table: (Optional) defaults to "fact2", name of fact table.
        fact_log: (Optional) defaults ot "fact_transaction", name of transaction log table.

    Returns:
        Nothing
    """

    def __init__(self, fact_table="fact2", fact_log="fact_transaction"):
        if not isinstance(fact_table, str):
            raise TypeError("fact table must be a string.")

        if not isinstance(fact_log, str):
            raise TypeError("fact log must be a string.")

        self._fact_table = fact_table
        self._fact_log = fact_log

        # Proclaim loudly into the void that we are loaded.
        super().__init__()
        logger.info("Fact Manager Initialized.")

    async def add(self, fact: Fact):
        """
        Adds a new fact to the database.  This will result in a ProgrammingError being thrown
        if a fact violates the (name, lang) Primary Key relationship.

        VERIFY IF THE FACT EXISTS WITH self.EXISTS() FIRST.

        Aliases cannot be inserted this way, at this time.  None is forced for fact.aliases.

        Args:
            fact: Fact Object to add.

        Returns:
            Nothing.

        Raises:
            TypeError: Attempt to commit incomplete Fact.
            pyscopg2.DatabaseError: Database Unavailable.
            psycopg2.IntegrityError: Primary Key violation on table.
        """
        # I said don't judge my SQL :(
        add_query = sql.SQL(f"INSERT INTO {self._fact_table} "
                            f"(name, lang, message, aliases, author, edited, editedby, mfd) "
                            f"VALUES ( %s, %s, %s, %s, %s, %s, %s, %s )")

        try:
            if not fact.complete:
                raise TypeError("Attempted commit on incomplete Fact.")

            add_values = (fact.name, fact.lang, fact.message, None,
                          fact.author, fact.edited, fact.editedby, fact.mfd)

            # run INSERT query
            await self.query(add_query, add_values)

        except (psycopg2.DatabaseError, psycopg2.IntegrityError) as error:
            # Database is not available, or fact already exists and wasn't checked.
            # Raise error, generating graceful cheese error and log the exception.
            logger.exception(f"Unable to add fact '{fact.name}!")
            raise error

    async def _destroy(self, name: str, lang: str):
        """
        Internal method to destroy a fact.  This is not to be invoked outside the delete
        method.

        Args:
            name: name of fact to destroy
            lang: langID of fact to destroy

        Returns: Nothing.
        """
        del_query = sql.SQL(f"DELETE FROM {self._fact_table} WHERE name=%s AND lang=%s")

        await self.query(del_query, (name, lang))

    async def delete(self, name: str, lang: str):
        """
        Deletes a fact from the database.  This is an un-recoverable action.  This must be done
        on a fact actually marked for deletion, using !factmfd.  Doing otherwise will result in
        a thrown psycopg2.ProgrammingError.

        Args:
            name: name of fact to be deleted
            lang: langID of fact to be deleted

        Returns: Nothing

        Raises: psycopg2.ProgrammingError if fact is not marked for deletion.
        """
        fact = await self.find(name, lang)

        # Check the fact's property to verify it is marked for deletion
        if fact is None or not fact.mfd:
            logger.exception("Attempted deletion of fact not marked for delete or does not exist.")
            raise psycopg2.ProgrammingError(f"{name}-{lang} is not marked for "
                                            f"deletion or does not exist")

        await self._destroy(name, lang)

    async def edit_message(self, name: str, lang: str, editor: str, new_message: str):
        """
        Edit a fact's message property on the database side.
        Generates a transaction log record.

        Args:
            name: name of fact
            lang: langID of fact
            editor: editor of fact (use context.user.nickname)
            new_message: New content of message property.

        Returns: Nothing

        Raises:
            psycopg2.ProgrammingError: On query failure.
            psycopg2.DatabaseError: On any connectivity issue or no database available.
        """
        if not await self.exists(name, lang):
            logger.exception("Attempted edit on non-existent fact.")
            raise ValueError

        try:
            current_fact = await self.find(name, lang)

            edit_query = sql.SQL(f"UPDATE {self._fact_table} SET message=%(message)s, "
                                 f"edited=%(edit_time)s WHERE name=%(name)s AND lang=%(lang)s")

            query_values = {"edit_time": datetime.datetime.now(datetime.timezone.utc),
                            "message": new_message, "name": name, "lang": lang}

            logger.debug(f"query_values = {query_values}")

            await self.query(edit_query, query_values)
        except (psycopg2.ProgrammingError, psycopg2.DatabaseError) as error:
            logger.exception(f"Editing fact '{name}-{lang}' failed.")
            raise error
        else:
            await self.add_transaction(fact_name=name, fact_lang=lang, author=editor, msg='Edited',
                                       new_field=new_message, old_field=current_fact.message)

    async def exists(self, name: str, lang: str) -> bool:
        """
        Check if a fact exists, without having to substantiate a full Fact object.

        Args:
            name: name of fact
            lang: language ID of fact

        Returns: True/False, if already exists.
        """
        query = sql.SQL(f"SELECT COUNT(*) message FROM "
                        f"{self._fact_table} WHERE name=%s AND lang=%s")

        try:
            result = await self.query(query, (name, lang))
        except (psycopg2.ProgrammingError, psycopg2.DatabaseError) as error:
            # Check for offline database, or issues with the query.
            logger.exception(f"Could not establish existence of {name}-{lang}")
            raise error

        # We are only getting a single integer as a response, so we can unpack it by index.
        # it will always return a single integer.
        return result[0][0]

    async def fact_history(self, fact_name: str, fact_lang: str) -> list:
        """
        Pulls the last 5 transaction logs for a fact, as a tuple

        Args:
            fact_name: Name of the fact
            fact_lang: LangID of the fact.

        Returns: tuple of transaction log items, for fact.
        """
        query = sql.SQL(f"SELECT name, lang, author, message, ts, old, new "
                        f"FROM {self._fact_log} WHERE name=%s AND lang=%s "
                        f"ORDER BY ts DESC LIMIT 5")

        query_data = (fact_name, fact_lang)

        try:
            result = await self.query(query, query_data)
        except (psycopg2.ProgrammingError, psycopg2.DatabaseError) as error:
            # ProgrammingError is a query failure, DatabaseError is database unavailable.
            logger.exception(f"Unable to retrieve history for {fact_name}-{fact_lang}")
            raise error

        return result

    async def find(self, name: str, lang: str) -> Fact:
        """
        Queries the database for a fact, and returns a populated Fact object.

        See Fact class for more information on Fact properties (Modules\fact.py)

        Args:
            name: name of fact to search, ie. 'prep'
            lang: language ID for fact, defaults to 'en' (see Fact Class)

        Returns: Fact()
        """
        # Build SQL Object for our query
        query = sql.SQL(f"SELECT name, lang, message, aliases, author, edited, editedby, mfd from "
                        f"{self._fact_table} where name=%s AND lang=%s")
        # await our raw result from query
        try:
            rows = await self.query(query, (name, lang))
        except (psycopg2.DatabaseError, psycopg2.ProgrammingError) as error:
            # Check for offline database, or query errors
            logger.exception("Unable to find fact due to exception.")
            raise error

        # unpack query into a fact object, or return None if there is no result.

        if rows:
            result = rows[0]
            return Fact(name=result[0],
                        lang=result[1],
                        message=result[2],
                        aliases=result[3],
                        author=result[4],
                        edited=result[5],
                        editedby=result[6],
                        mfd=result[7])

    async def add_transaction(self, fact_name: str, fact_lang: str, author: str, msg: str,
                              new_field=None, old_field=None):
        """
        Writes a transaction log entry to the transaction log table.
        The msg field should be only be one of the following (by convention):

        * Added
        * Deleted
        * Edited
        * Marked for delete
        * Unmarked for delete

        Args:
            fact_name: Name of fact this applies to.
            fact_lang: langID of fact this applies to.
            author: the user that triggered the log entry.
            msg: Message to be written to log.
            new_field: Contents to place in the 'new' field for the log row.
            old_field: Contents to place in the 'old' field for the log row.

        Returns: Nothing.
        """
        log_query = sql.SQL(f"INSERT INTO {self._fact_log} "
                            f"(name, lang, author, message, old, new, ts) "
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s)")

        query_data = (fact_name, fact_lang, author, msg, old_field, new_field,
                      datetime.datetime.utcnow())

        try:
            await self.query(log_query, query_data)
        except (psycopg2.ProgrammingError, psycopg2.DatabaseError) as error:
            logger.exception("Unable to write transaction log to table.")
            raise error

    async def mfd(self, name: str, lang: str) -> bool:
        """
        Toggles the 'marked for deletion' flag on a fact.


        Args:
            name: name of fact to update
            lang: lang of fact to update

        Returns:
            bool: True/False that fact was set to.
        """

        query = sql.SQL(f"SELECT mfd FROM "
                        f"{self._fact_table} WHERE name=%s AND lang=%s")

        mfd_query = sql.SQL(f"UPDATE {self._fact_table} "
                            f"SET mfd=%s WHERE name=%s AND lang=%s")

        try:
            result = await self.query(query, (name, lang))

            # Invert MFD field value, and set it again.
            mfd_value = not result[0][0]
            await self.query(mfd_query, (mfd_value, name, lang))

        except (psycopg2.ProgrammingError, psycopg2.DatabaseError) as error:
            # ProgrammingError is a query failure, DatabaseError is database unavailable.
            logger.exception(f"Error setting MFD field value for {name}-{lang}")
            raise error

        return mfd_value

    async def mfd_list(self, num_results=5) -> list:
        """
        Returns a list of facts marked for deletion.

        Args:
            num_results: (Optional) number of results to return. Default 5.

        Returns:
            list: facts marked for deletion.
        """
        query = sql.SQL(f"SELECT name, lang FROM "
                        f"{self._fact_table} WHERE mfd=%s "
                        f"ORDER BY edited DESC LIMIT {num_results}")

        try:
            raw_results = await self.query(query, (True,))
        except (psycopg2.ProgrammingError, psycopg2.DatabaseError) as error:
            # ProgrammingError is a query failure, DatabaseError is database unavailable.
            logger.exception(f"Error getting MFD list.")
            raise error
        else:
            result = [f"{item[0]}-{item[1]}" for item in raw_results]

        return result
