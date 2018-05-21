#
#Dockerfile - build script for the mechasqueak3 irc bot
#    this script will create the runtime environment necessary to run the bot and, by default
#    invocation, run the Unit Tests.
#
#Copyright (c) 2018 The Fuel Rats Mischief,
#All rights reserved.
#
#Licensed under the BSD 3-Clause License.
#
#See LICENSE.md
#


# Use an official Python runtime as a parent image
FROM python:3.6.5-alpine

COPY ./requirements.txt ./
# fetch git, as we will need it.
RUN apk add --no-cache git

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r /requirements.txt

# Copy the current directory contents into the container at /app
ADD . /mechasqueak

# Set the working directory to /mechasqueak
WORKDIR /mechasqueak
