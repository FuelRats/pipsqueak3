#!/bin/bash
# get the current commit from git
GIT_HASH=git rev-parse --short HEAD
echo "GIT_HASH=${GIT_HASH}"
GIT_HASH_SHORT=${GIT_HASH:0:7}
echo "GIT_HASH_SHORT=${GIT_HASH_SHORT}"
echo "##teamcity[buildNumber '${GIT_HASH_SHORT}']"