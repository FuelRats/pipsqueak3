#
#Dockerfile - build script linting mechasqueak3 irc bot
# this script will run the linting suite
#
#Copyright (c) 2018 The Fuel Rat Mischief,
#All rights reserved.
#
#Licensed under the BSD 3-Clause License.
#
#See LICENSE.md
FROM mechasqueak:latest

# install linting deps
RUN curl -o pylint-exit https://raw.githubusercontent.com/theunkn0wn1/pylint-exit/master/pylint_exit.py
RUN  pipenv run pip install bitarray
