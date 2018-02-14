# pipsqueak
ED Fuel rats [sopel](http://sopel.chat) module package

[![Build Status](https://travis-ci.org/FuelRats/pipsqueak.svg?branch=mecha3)](https://travis-ci.org/FuelRats/pipsqueak)

# The below information is extremely outdated.

# Requirements

## Python 3.6
In addition to Python 3.6 itself, pipsqueak uses the following modules which will be installed
 for you during part of the setup process:
 
- **Pydle** for the bot framework itself
- **requests** for API calls and fetching EDSM system data.
- **iso8601** for date parsing.
- **sqlalchemy** for database access.
- **alembic** for database schema creation/migration across updates.
- **psycopg2** for PostgreSQL database support in SQLAlchemy and Alembic.

You may need to install the development versions of the PostgreSQL client libraries to build psycopg2 on your platform.

You will need to install the `Asyncio` branch of Pydle, **NOT** the master / pip varient.
## PostgreSQL
All testing has been performed with version 9.5.1.  Versions as low as 9.1 should theoretically work.  Versions earlier
 then that may also work with some updates to the query used by bot's !search command.
 
PostgreSQL will need:
- A user account for the bot.
- A database instance owned by that user.
- The [fuzzystrmatch](http://www.postgresql.org/docs/9.5/static/fuzzystrmatch.html) extension loaded into the bot's 
  database.  This is included with PostgreSQL, though it may require installation of your platform's postgresql-contrib package or similar.  It can be added by any superuser with `CREATE EXTENSION fuzzystrmatch;`

### Alternate database options
Theoretically, another database can be used instead of PostgreSQL provided that SQLAlchemy and Alembic support it.
Using another database will require adjusting the query used in !search to use an appropriate fuzzy-matching function,
and has some possible issues when refreshing the systemlist.

There are potential locking issues with SQLite and possibly MySQL, notably during the couple of minutes it takes to
refresh the starsystem list.

# Installation instructions
Requires Pydle to be installed using its `asyncio` branch, clone [its repository](https://github.com/Shizmob/pydle/tree/asyncio), checkout the `asyncio` branch, and run its `setup.py`
## Acquiring source
`git clone https://github.com/FuelRats/pipsqueak.git`

## Create a virtual environment
1. Most Python distributions include a built-in module for creating virtualenvs.  If yours does not:
  - `# pip install virtualenv`   
2. `# cd pipsqueak`
3. `# python -m venv *PATH*` or `virtualenv *PATH*` 
  - *PATH* can be . to create the virtualenv in the current directory.  Using 'venv' as a path is also fine, and will ensure virtual environment files are ignored by git.
	
## Configure the bot
**_TODO:_** write config stuff. 
   
## Activate the virtual environment and install dependencies
1. `# source *PATH*/bin/activate`
2. `# pip install -r requirements.txt`

## Start the bot   
1. `# source *PATH*/bin/activate`
2.  `python main.py`