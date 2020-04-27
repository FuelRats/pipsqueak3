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

# Copy the current directory contents into the container at /mechasqueak
ADD . /mechasqueak

# PEP517 install
RUN pip install /mechasqueak
