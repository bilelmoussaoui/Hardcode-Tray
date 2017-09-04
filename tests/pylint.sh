SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
find $SITE_PACKAGES/HardcodeTray/ -name "*.py" | xargs pylint --rcfile=../.pylintrc $1
