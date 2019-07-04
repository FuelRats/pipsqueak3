#
#Dockerfile - development dockerfile for SPARK
# expands the base ( production ) mecha image with development dependencies
#
#Copyright (c) 2018 The Fuel Rat Mischief,
#All rights reserved.
#
#Licensed under the BSD 3-Clause License.
#
#See LICENSE.md

# there is no sensible base image, so set it to something invalid as to intentionally break things
# this arg MUST be provided via --build-arg base_image=
# and set to something sensible (that exists on the build host).

ARG base_image=CHANGE/ME
FROM mecha:$base_image

WORKDIR /mechasqueak
RUN apk add --no-cache curl bash
RUN \
 apk add --no-cache --virtual .build-deps gcc musl-dev&& \
 pip install bitarray&& \
 pipenv install --system -d &&\
 apk --purge del .build-deps

# install linting deps
RUN curl -o pylint-exit https://raw.githubusercontent.com/theunkn0wn1/pylint-exit/master/pylint_exit.py
