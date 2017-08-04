#!/usr/bin/env sh
find $1 -name "*.py" | xargs pylint --rcfile=../.pylintrc $1