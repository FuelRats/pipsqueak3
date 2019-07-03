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
FROM python:3.7.3-alpine
# Set the working directory to /mechasqueak
WORKDIR /mechasqueak
ENV PIPENV_VENV_IN_PROJECT True

COPY ./Pipfile ./
COPY ./Pipfile.lock ./

RUN pip install pipenv

# psql install shit
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 pipenv install -d && \
 apk --purge del .build-deps

# Copy the current directory contents into the container at /mechasqueak
ADD . /mechasqueak

CMD pipenv run python -m src