#!/usr/bin/env bash
function check_cwd() {
  echo "##teamcity[blockOpened name='Check working directory...']"
  echo "my working directory is ${PWD}"
  if [[ $PWD != "/mechasqueak" ]]; then
    echo "working directory mismatch!"
    echo "##teamcity[message text='Working directory is WRONG! check the configs. executing in $PWD but expected /mechasqueak' status='WARNING']"
    echo "attempting to correct path...."
    cd /mechasqueak
  fi
  echo "##teamcity[blockClosed name='Check working directory...']"
}