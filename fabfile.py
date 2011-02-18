import os
from fabric.api import *


def scrub():
    """ Death to the bytecode! """
    local('rm -fr dist build')
    local("find . -name \"*.pyc\" -exec rm '{}' ';'")

def docs():
    """Build docs."""
    os.system('make dirhtml')
    os.chdir('_build/dirhtml')
    os.system('sphinxtogithub .')
    os.system('git add -A')
    os.system('git commit -m \'documentation update\'')
    os.system('git push origin gh-pages')