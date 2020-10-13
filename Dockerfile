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
FROM python:3.8.5
# Set the working directory to /mechasqueak
WORKDIR /mechasqueak

COPY ./pyproject.toml /mechasqueak
COPY ./poetry.lock /mechasqueak
# fetch git, as we will need it.
RUN apt update && apt install -y git build-essential

# install pipenv
WORKDIR /mechasqueak
RUN pip install poetry
RUN poetry install --no-root
# Copy the current directory contents into the container at /mechasqueak
ADD . /mechasqueak

RUN poetry run pip install .


