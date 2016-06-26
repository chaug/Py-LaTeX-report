#!/usr/bin/env python

if __name__ != "__main__":
	print "Should be run as main!!"
	exit(255)

import os
import sys
import site

SHELL_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__)))
PYTHON_SITE = os.path.abspath(os.path.join(SHELL_PATH, '..', 'src', 'python'))

site.addsitedir(PYTHON_SITE)

from pytex.core.management import execute_from_command_line

execute_from_command_line(sys.argv)
