# pipsqueak
ED Fuel rats [sopel](http://sopel.chat) module package

# The below information is outdated, but will be updated soon™

# Requirements

## Python 3.4
In addition to Python 3.4 itself, pipsqueak uses the following modules which will be installed
 for you during part of the setup process:
 
- **Sopel** for the bot framework itself
- **requests** for API calls and fetching EDSM system data.
- **iso8601** for date parsing.
- **sqlalchemy** for database access.
- **alembic** for database schema creation/migration across updates.
- **psycopg2** for PostgreSQL database support in SQLAlchemy and Alembic.

You may need to install the development versions of the PostgreSQL client libraries to build psycopg2 on your platform.

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
Requires Sopel to be installed, for more information on this see [Sopel's website](http://sopel.chat/download.html).  Following the virtualenv setup procedure should install sopel.

## Acquiring source
`git clone https://github.com/FuelRats/pipsqueak.git`

## Create a virtual environment
1. Most Python distributions include a built-in module for creating virtualenvs.  If yours does not:
  - `# pip install virtualenv`   
2. `# cd pipsqueak`
3. `# python -m venv *PATH*` or `virtualenv *PATH*` 
  - *PATH* can be . to create the virtualenv in the current directory.  Using 'venv' as a path is also fine, and will ensure virtual environment files are ignored by git.
	
## Configure the bot
1. Copy sopel.cfg-dist to sopel.cfg
  - `# cp sopel.cfg-dist sopel.cfg`
2. Edit sopel.cfg
  - `# vim sopel.cfg`
   
## Activate the virtual environment and install dependencies
1. `# source *PATH*/bin/activate`
2. `# pip install -r requirements.txt`

## Start the bot   
1. `# source *PATH*/bin/activate`
2. `# python start.py -c sopel.cfg`
  - **Using the built-in sopel command is not recommended, as it won't set PYTHONPATH correctly for imports.**

# rat-search.py
## Commands
Command    | Parameters | Explanation
--- | --- | ---
`search`     | System     | Searches for the given system in the system database.
`sysstats`   |            | Returns some statistics on the current system database.  (Temporary command for debugging)
`sysrefresh` |            | Rebuilds the system database by pulling new data from EDSM, provided the existing data is old enough (12 hours by default).
             | -f         | Does the above, regardless of the age of the existing data.
             
sysstats and sysrefresh exist mainly for debugging and will probably go away or be redesigned in a later build.
             
## Detailed module information
The system search compares the input with a large list of systems,
downloaded from EDSM, if no list present this will fail.

# rat-board.py
## Commands

*ref* in the below table refers to a reference to a case.  This can be: the client's nickname, the client's CMDR name (if known), a case number, or a case API ID (beginning with an `@`-sign)

Commands that add quotes to a case will create a new case when *ref* looks like a nickname or CMDR name and no active case can be found.  
 
Command | Parameters | Explanation
--- | --- | ---
`quote` | *ref* | Recites all information on `Nick`'s case.
`clear`, `close` | *ref* | Mark the referenced case as closed.
`list` | | List the currently active cases.
 | -i | Also list open, inactive cases.
 | -@ | Show API IDs in the list in addition to case numbers.
`grab` | Nick | Grabs the last message `Nick` said and add it to their case, creating one if it didn't already exist.
`inject` | *ref*, message | Injects a custom message into the referenced case's quotes.  Creates the case if it doesn't already exist.
`sub` | *ref*, index, [message] | Substitute or delete line `index` to the referenced case.
`active`, `activate`, `inactive`, `deactivate`| *ref* | Toggle the referenced case between inactive and active.  Despite the command names, all of these perform the same action (e.g. `deactivate` will happily re-activate an inactive case) 
`assign`, `add`, `go` | *ref*, rats... | Assigns `rats` to the referenced case.  Separate rats with spaces.
`unassign`, `deassign`, `rm`, `remove`, `standdown` | *ref*, rats... | Removes `rats` from the referenced case if they were assigned to it.
`cr`, `codered`, `casered` | *ref* | Toggle the code red status of the referenced case.
`pc` | *ref* | Sets the referenced case to be in the PC universe.
`xbox`, `xb`, `xb1`, `xbone`, `xbox1` | *ref* | Set the referenced case to be in the Xbox One universe.

## Detailed module information
pipsqueak includes a tool to keep track of the current board of rescues, called 'cases'.

Every message that starts with the word 'ratsignal' (case insensitive) is
automatically used to create a new case.

## Bonus Features

Ratsignals and lines added with `inject` perform some behind-the-scenes magic when they add lines to a case:

- If the system coordinates trigger System Name Autocorrection, the system name is automatically corrected and an
  additional line is added to the case indicating the correction.  This fixes simple cases of accidental letter/number 
  substitution in procedurally-generated system names, but does not otherwise guarantee the system name is correct.
- If the platform is unknown and a new line contains 'PC' as a whole word somewhere, the platform is automatically set
  to PC.  If a new line contains XB, XBox, XB1, Xbone, XboxOne, Xbox1, XB-1, or any of several other variations, the
  platform is automatically set to XBox.  If a line matches both the PC and XBox patterns, the platform is unchanged.

In all situations where this magic occurs, the bot' confirmation message will tell you about it.  For instance, a new
case where the system name was corrected and platform autodetected will end with something like 
`(Case 4, autocorrected, XB)`

`sub` does *not* perform any of this magic, and may be used to correct the bot in the unlikely case of false positives.

# rat-facts.py

## Commands
Command | Parameters | Explanation
--- | --- | ---
`fact` / `facts` | | Shows a list of all known facts.
 | *fact* | Reports translation statistics on the listed fact.
 | *fact* `full` | As above, but also PMs you with all translations.
 | *lang* | Reports translation statistics on the listed language.
 | *lang* `full` | As above, but also PMs you with all facts in that language.

## Privileged Commands
Commands listed here are only usable if you have halfop or op on any channel the bot is joined to.
You do not need to send the command from that channel, but must be currently joined to it.

Command | Parameters | Explanation
--- | --- | ---
`fact` / `facts` | (add|set) *fact*-*lang* *message* | Adds a new fact to the database, replacing the old version if it already existed.
`fact` / `facts` | (del[ete]|remove) set *fact*-*lang* | Deletes a fact from the database.
`fact` / `facts` | import | Tells the bot to (re)import legacy JSON files into the database.  This will not overwrite existing facts.

## Config
Name | Purpose | Example
--- | --- | ---
filename | the name (and absolute path) to the JSON file containing the facts, or a directory containing .json files.  Any files found will be imported to the database on startup | /home/pipsqueak/facts.json
lang | Comma-separated list of languages to search for facts when no language specifier is present. | en,es,de,ru

## Detailed module information
Scans incoming message that start with ! for keywords specified in the database and replies with the appropriate response.  Also allows online editing of facts.

If the language search order is "en,es":
* `!xwing`: Searches for the 'xwing' fact using the default search order (English, Spanish).  The `fact` command will display matching facts as **xwing-en** and **xwing-es**.
* `!xwing-es`: Searches for the 'xwing' fact in Spanish first.  If this fails, falls back to the default search order.
* `!xwing-ru`: Searches for the 'xwing' fact in Russian first.  If this fails, falls back to the default search order.

When adding or deleting facts the full fact+language specifier must be used (`xwing-en` rather than `xwing`).  `fact` will tell you this if you forget.

# rat-drill.py
## Commands
Command | Parameters | Explanation
--- | --- | ---
`drill` | | Print out both drill lists.
 | `-b` | See above
 | `-r` | Print only the [R]atting drills list.
 | `-d` / `-p` | Print only the [D]is[P]atch drills list.
`drilladd` | -r `name` | Add `name` to the [R]atting drills list.
 | -d `name` / -p `name` | Add `name` to the [D]is[P]atch drills list.
 | -b `name` | Add `name` to [B]oth the ratting and dispatch drills list.
`drillrem` | `name` | Remove `name` from both drill lists (if applicable).
 | | To remove `name` from only 1 list, use `drilladd`

## Config
Name | Purpose | Example
--- | --- | ---
drilllist | The name of the JSON file containing the drill lists | drills.json

# rat-socket.py
## Commands
Command    | Parameters | Explanation
--- | --- | ---
`connect` `connectsocket`     |   none   | Connects to the configured Websocket Server and starts dumping information to chat

## Config
Name | Purpose | Example
--- | --- | ---
websocketurl | The URL of the WebSocket to connect to | ws://dev.api.fuelrats.com
websocketport | The Port of the WebSocket to connect to | 80
             
## Detailed module information
Used to Connect to the WebSocket Part of the API to listen for Updates from RatTracker. Currently only Dumping gotten messages into Chat only though.
Will Attempt to reconnect to the WebSocket if the initial connection fails or the connection gets lost at any point. If a reconnect fails, it will retry indefinitely with an always increasing delay which grows exponentially. 
