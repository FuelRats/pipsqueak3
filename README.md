<img src="https://github.com/FuelRats/pipsqueak3/blob/develop/assets/m3spark.png?raw=true" width="50%" />

[![Build Status](https://travis-ci.org/FuelRats/pipsqueak3.svg?branch=develop)](https://travis-ci.org/FuelRats/pipsqueak3) [![Maintainability](https://api.codeclimate.com/v1/badges/83b536889d48ddfe2557/maintainability)](https://codeclimate.com/github/FuelRats/pipsqueak3/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/83b536889d48ddfe2557/test_coverage)](https://codeclimate.com/github/FuelRats/pipsqueak3/test_coverage)

SPARK is the all-in-one wonderbot written and utilized by *The Fuel Rat* for rescue management.
This project is under active development.  As such, features may be added or removed without notice.

SPARK is currently **incomplete**.

## Requirements
* Python 3.6.x
* Postgres server
* [Pydle, asyncio branch](https://github.com/Shizmob/pydle/tree/asyncio) ``git://github.com/Shizmob/pydle.git@asyncio#egg=pydle``

## Installation
This script can be run as either a Dockerized service or run locally.

To run as a docker image, you may use the provided docker-compose.

If you would prefer to run the service locally, bare in mind you may need to run a local 
Postgres Database for mecha's fact module.
###Building via Docker
We have provided a `docker-compose.yml` suitably configured for building and running mechasqueak
as a Alpine Linux multi-container service. 

To build Mechasqueak via docker, run the following command:
```bash
docker-compose build mechasqueak
```

To verify the build completed successfully and you have a clean copy of the project, please run
the test suites.
```bash
docker-compose run tests
```

To run the bot, after creating your configuration file (see Configuration below), run the following
command:
```bash
docker-compose run mechasqueak
```
## Configuration
Configuration settings are stored in the `config/` subfolder as JSON files. 

By default, Mecha will attempt to load `configuration.json` (file not provided) from this subdirectory.

To configure mecha locally, please copy the provided `config.template.json` to a new file
`configuration.json` and fill in the appropriate fields, see `config/configuration.md` for details.

please note that, when run via docker, it is not necessary to rebuild the image after changing
configuration options as that directory is shared with the container (see `config/configuration.md`)