import os
from fabric.api import *


def scrub():
	""" Death to the bytecode! """
	local('rm -fr dist build')
	local("find . -name \"*.pyc\" -exec rm '{}' ';'")

def docs():
	"""Build docs."""
	os.system('make html')
	os.system('cd _build/html')
	os.system('git commit -am \'documentation update\'')
	os.system('git push origin gh-pages')