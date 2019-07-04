#!/bin/bash
BUILD_NUMBER=%build.number%
echo "BUILD_NUMBER=${BUILD_NUMBER}"
GIT_HASH=%build.vcs.number%
echo "GIT_HASH=${GIT_HASH}"
GIT_HASH_SHORT=${GIT_HASH:0:7}
echo "GIT_HASH_SHORT=${GIT_HASH_SHORT}"
echo "##teamcity[buildNumber '${GIT_HASH_SHORT}']"