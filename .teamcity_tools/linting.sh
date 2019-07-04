#!/usr/bin/env bash
echo "ls -a..."
ls -a
echo "running pylint"....
pylint src || python pylint-exit $?
echo "running pycodestyle..."
pycodestyle src
echo "done!"