#!/usr/bin/env python3

from os import environ, path
from subprocess import call

prefix = environ.get('MESON_INSTALL_PREFIX', '/usr/local')
destdir = environ.get('DESTDIR', '')

if not destdir:
    call(['chmod', '+x', path.join(prefix, 'bin', 'hardcode-tray')])
