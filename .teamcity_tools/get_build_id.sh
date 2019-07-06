#!/bin/bash
# get current commit from git
GIT_HASH="$(git rev-parse --short HEAD)"
echo "full commit hash: ${GIT_HASH}"
GIT_HASH_SHORT="${GIT_HASH:0:7}"
echo "output hash : ${GIT_HASH_SHORT}"
echo "##teamcity[sha_2 '${GIT_HASH_SHORT}']"