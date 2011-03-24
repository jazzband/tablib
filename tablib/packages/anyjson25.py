u"""
Wraps the best available JSON implementation available in a common interface
"""

__version__ = u"0.2.0"
__author__ = u"Rune Halvorsen <runefh@gmail.com>"
__homepage__ = u"http://bitbucket.org/runeh/anyjson/"
__docformat__ = u"restructuredtext"

u"""

.. function:: serialize(obj)

    Serialize the object to JSON.

.. function:: deserialize(str)

    Deserialize JSON-encoded object to a Python object.

.. function:: force_implementation(name)

    Load a specific json module. This is useful for testing and not much else

.. attribute:: implementation

    The json implementation object. This is probably not useful to you,
    except to get the name of the implementation in use. The name is
    available through `implementation.name`.
"""

import sys
from itertools import izip

implementation = None

u"""
.. data:: _modules

    List of known json modules, and the names of their serialize/unserialize
    methods, as well as the exception they throw. Exception can be either
    an exception class or a string.
"""
_modules = [(u"cjson", u"encode", u"EncodeError", u"decode", u"DecodeError"),
            (u"jsonlib2", u"write", u"WriteError", u"read", u"ReadError"),
            (u"jsonlib", u"write", u"WriteError", u"read", u"ReadError"),
            (u"simplejson", u"dumps", TypeError, u"loads", ValueError),
            (u"json", u"dumps", TypeError, u"loads", ValueError),
            (u"django.utils.simplejson", u"dumps", TypeError, u"loads",
             ValueError)]
_fields = (u"modname", u"encoder", u"encerror", u"decoder", u"decerror")


class _JsonImplementation(object):
    u"""Incapsulates a JSON implementation"""

    def __init__(self, modspec):
        modinfo = dict(list(izip(_fields, modspec)))

        # No try block. We want importerror to end up at caller
        module = self._attempt_load(modinfo[u"modname"])

        self.implementation = modinfo[u"modname"]
        self._encode = getattr(module, modinfo[u"encoder"])
        self._decode = getattr(module, modinfo[u"decoder"])
        self._encode_error = modinfo[u"encerror"]
        self._decode_error = modinfo[u"decerror"]

        if isinstance(modinfo[u"encerror"], unicode):
            self._encode_error = getattr(module, modinfo[u"encerror"])
        if isinstance(modinfo[u"decerror"], unicode):
            self._decode_error = getattr(module, modinfo[u"decerror"])

        self.name = modinfo[u"modname"]

    def _attempt_load(self, modname):
        u"""Attempt to load module name modname, returning it on success,
        throwing ImportError if module couldn't be imported"""
        __import__(modname)
        return sys.modules[modname]

    def serialize(self, data):
        u"""Serialize the datastructure to json. Returns a string. Raises
        TypeError if the object could not be serialized."""
        try:
            return self._encode(data)
        except self._encode_error, exc:
            raise TypeError(*exc.args)

    def deserialize(self, s):
        u"""deserialize the string to python data types. Raises
        ValueError if the string vould not be parsed."""
        try:
            return self._decode(s)
        except self._decode_error, exc:
            raise ValueError(*exc.args)


def force_implementation(modname):
    u"""Forces anyjson to use a specific json module if it's available"""
    global implementation
    for name, spec in [(e[0], e) for e in _modules]:
        if name == modname:
            implementation = _JsonImplementation(spec)
            return
    raise ImportError(u"No module named: %s" % modname)


for modspec in _modules:
    try:
        implementation = _JsonImplementation(modspec)
        break
    except ImportError:
        pass
else:
    raise ImportError(u"No supported JSON module found")

serialize = lambda value: implementation.serialize(value)
deserialize = lambda value: implementation.deserialize(value)
