#!/usr/bin/env bash

# import check CWD n stuff from linting
source /mechasqueak/.teamcity_tools/shared_lib.sh

check_cwd

echo "##teamcity[blockOpened name='Execute test suite']"
pytest src
echo "##teamcity[blockClosed name='Execute test suite']"