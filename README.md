<img src="https://github.com/FuelRats/pipsqueak3/blob/develop/assets/m3spark.png?raw=true" width="50%" />

[![Build Status](https://circleci.com/gh/FuelRats/pipsqueak3/tree/develop.svg?style=svg)](https://circleci.com/gh/FuelRats/pipsqueak3/tree/develop) 

SPARK is the all-in-one wonderbot written and utilized by *The Fuel Rats* for rescue management.
This project is under active development.  As such, features may be added or removed without notice.

> As this project is under heavy development, we cannot offer support at this time.  However, please do report bugs or issues on our project [here.](http://t.fuelr.at/help)

SPARK is currently **incomplete**.

## Requirements
* Python 3.8
* PostgreSQL
* `poetry`
## Installation
This script can be run as a Docker image or run locally.

To run as a docker image, you may use the provided docker-compose.

If you would prefer to run the service locally, bear in mind you may need to run a local PostgreSQL Database for the fact module.

### Building via Docker
We have provided a `docker-compose.yml` suitably configured for building and running Mecha
as a Alpine Linux multi-container service. 

## Run with Docker
To build Mecha via docker, run the following command:
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

## Run Locally
> ## NOTE:
> on top of pip you must have installed `poetry`, this guide assumes this fact.

> If you are not using poetry, please see [pyproject.toml](pyproject.toml) for the list of required libraries. 
 You will need to install these libraries manually.

1. Clone the repository from the ``master`` branch, or for bleeding edge, use ``develop``.  Please keep in mind, Develop changes frequently and may be broken.
2. Install the project's requirements, `poetry install --no-root`
3. once installed, activate the venv `poetry shell`
4. Build your configuration file.  Please see the [Configuration](#Configuration) section.
5. Execute Mecha with ``python -m src --config <your configuration file>``  (You may need to use the python3 alias)

|    Flag         |    Description                     |
| :--------------:|------------------------------------|
| --clean-log     | New log file.  Old one is deleted. |
| --config-file file.json   | Use configuration file _file.json_      |
| --verbose |  Verbose mode. (Logging level set to Debug) |
| --nocolors | Disable ANSI color coding in console. |

## Configuration
Configuration settings are stored in the `config/` subfolder as JSON files. 

By default, Mecha will attempt to load `configuration.toml` (file not provided) from this subdirectory.

To configure Mecha locally, please copy the provided `config.template.toml` to a new file.
`configuration.toml` and fill in the appropriate fields, see `config/configuration.md` for details.

When run via docker, it is not necessary to rebuild the image after changing
configuration options as that directory is shared with the container (see `config/configuration.md`)
