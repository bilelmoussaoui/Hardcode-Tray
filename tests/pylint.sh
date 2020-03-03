#!/usr/bin/env sh
SITE_PACKAGES=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
find "$SITE_PACKAGES"/HardcodeTray/ -name '*.py' | xargs pylint --rcfile=.pylintrc $1
