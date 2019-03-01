"""
fact_table_converter.py - Converts Fact Tables to Fact2 format.

Creates the new schema for mecha3's version of the Fact Manager, and converts
existing facts to the new format.

NULL entries will have default values inserted.

This script is STANDALONE and is not intended to be invoked by mecha.
Do not import this file, or build a command to invoke it via IRC.

It will halt if the fact2 table or the log table already exists.
Delete these manually if they already exist before execution.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

"""
import psycopg2
import getpass

from psycopg2 import pool


if __name__ == "__main__":
    # CLI Warning
    print("===============Fact Table Conversion Tool=================")
    print("Converts Fact v1 tables to Fact v2")
    print("DO NOT RUN THIS UNLESS YOU KNOW WHAT YOU ARE DOING.")
    print("")
    print("Press Enter to continue.")
    input()
    print("CONNECTION SETTINGS:")
    database_host = input("Database Host Address [localhost]:") or "localhost"
    database_port = input("Database Port [5432]:") or "5432"
    database_name = input("Database Name [mecha3]:") or "mecha3"
    database_user = input("Database User [mecha3]:") or "mecha3"
    database_pass = getpass.getpass("Database Password [mecha3]:") or "mecha3"
    print("TABLE SETTINGS:")
    old_fact_table = input("Old Table Name [fact]:") or "fact"
    new_fact_table = input("New Table Name [fact2]:") or "fact2"
    print("")
    print("Summary:")
    print(f"Connecting to '{database_host}:{database_port}'")
    print(f"Username: {database_user}")
    print(f"Convert From {old_fact_table} to new table {new_fact_table}")
    do_continue = input("Do you wish to continue [N]?") or "N"
    if do_continue != "Y":
        print("Quitting, User chose not to continue.")
        quit()

    # Establish Database Connection
    try:
        database_pool = psycopg2.pool.SimpleConnectionPool(1, 5, host=database_host,
                                                           port=database_port,
                                                           dbname=database_name,
                                                           user=database_user,
                                                           password=database_pass
                                                           )

    except (psycopg2.DatabaseError, psycopg2.ProgrammingError) as error:
        print("Unable to connect to database. Please check connection settings and try again.")
        raise error

    with database_pool.getconn() as connection:
        connection.autocommit = True
        connection.set_client_encoding('utf-8')

        with connection.cursor() as cursor:

            # Pull the number of facts in the database:
            cursor.execute(f"SELECT COUNT(*) FROM {old_fact_table}")
            count_result = cursor.fetchall()
            bar_count = count_result[0][0]
            print(f"Found {bar_count} facts in the old table.")

            # Check if the new fact table already exists, and bail if it does.
            cursor.execute(f"SELECT relname FROM pg_class WHERE relname='{new_fact_table}'")
            table_check = cursor.fetchall()
            if table_check:
                print(f"ERROR: Destination table '{new_fact_table}' exists.")
                print("Either you already converted, or need to drop the table from a failed run.")
                quit()
            else:
                cursor.execute(f"CREATE TABLE {new_fact_table} (name VARCHAR NOT NULL, "
                               f"lang VARCHAR NOT NULL, message VARCHAR NOT NULL, "
                               f"aliases TSVECTOR, author VARCHAR, "
                               f"edited TIMESTAMP WITH TIME ZONE, editedby "
                               f"VARCHAR, mfd BOOLEAN, "
                               f"CONSTRAINT {new_fact_table}_pkey PRIMARY KEY (name, lang))")
                print(f"Created New Table {new_fact_table}.")

            # Create the log table too, if it doesn't already exist.
                cursor.execute(f"CREATE TABLE IF NOT EXISTS fact_transaction "
                               f"(id SERIAL, name VARCHAR NOT NULL,"
                               f" lang VARCHAR NOT NULL, author VARCHAR NOT NULL, "
                               f"message VARCHAR NOT NULL, old VARCHAR, "
                               f"new VARCHAR, ts TIMESTAMP WITH TIME ZONE, "
                               f"CONSTRAINT fact_transaction_pkey PRIMARY KEY (id))")
                print(f"Created new log table 'fact_transaction'")

                # Pull ALL the old facts into a result var.
                cursor.execute(f"SELECT name, lang, message, author FROM {old_fact_table}")
                old_facts = cursor.fetchall()

                # Actual conversion loop is rather simple.
                for fact in old_facts:
                    # Convert empty author field to default
                    if fact[3] is None:
                        fact[3] = 'The Fuel Rats'

                    # Do Actual conversion here:
                    cursor.execute(f"INSERT INTO {new_fact_table} "
                                   f"(name, lang, message, aliases, author, edited, editedby, mfd) "
                                   f"VALUES (%(name)s, %(lang)s, %(message)s, NULL, "
                                   f"%(author)s, '1970-1-1 00:00:00-00', %(author)s, FALSE)",
                                   {"name": fact[0], "lang": fact[1],
                                    "message": fact[2], "author": fact[3]})

                print("If nothing died and blew chunks...SUCCESS!")
                print(f"The old table '{old_fact_table}' has not been removed. Back it up first.")
                quit()
