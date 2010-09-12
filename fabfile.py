from fabric.api import *


def scrub():
	""" Death to the bytecode! """
	local("rm -fr dist build")
	local("find . -name \"*.pyc\" -exec rm '{}' ';'")
