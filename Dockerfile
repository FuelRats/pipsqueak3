#
#Dockerfile - build script for the mechasqueak3 irc bot
#    this script will create the runtime environment necessary to run the bot and, by default
#    invocation, run the Unit Tests.
#
#Copyright (c) 2018 The Fuel Rat Mischief,
#All rights reserved.
#
#Licensed under the BSD 3-Clause License.
#
#See LICENSE.md
#


# Use an official Python runtime as a parent image
FROM python:3.8.2-buster
# Set the working directory to /mechasqueak
WORKDIR /mechasqueak

COPY ./poetry.lock ./
COPY ./pyproject.toml ./

# fetch git, as we will need it.
RUN apt install git

# install poetry
RUN pip install poetry

# TEMPFIX: open bug with poetry in a docker container (https://github.com/python-poetry/poetry/issues/1899)
# The following commands work around this bug and install faster using pip
RUN poetry config virtualenvs.create false \
                && poetry export --without-hashes -f requirements.txt --dev \
                |  poetry run pip install -r /dev/stdin \
                && poetry debug
COPY . ./
RUN poetry install --no-interaction

# Copy the current directory contents into the container at /mechasqueak
ADD . /mechasqueak

