from fabric.api import *


def scrub():
	""" Death to the bytecode! """
	local("rm -fr dist build")
	local("find . -name \"*.pyc\" -exec rm '{}' ';'")
	
def test():
	""" Test parsing! """
	local("rm output/*")
	local("./strata.py --nsanity_files 'strata/tests/samples/nsanity' -d")
	
def build():
	""" Build application"""
	pass
	
def init():
	""" Initialize Environment """
	# TODO: Possibly add Virtual Environment?
	local("sudo pip install -r REQUIREMENTS")
	
if __name__ == '__main__':
	# TODO: Remove (for testing purposes)
	# TODO: [Possibly] add doctests
	test()
	