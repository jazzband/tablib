"""
Wraps the best available JSON implementation available in a common interface
"""

__version__ = "0.2.0"
__author__ = "Rune Halvorsen <runefh@gmail.com>"
__homepage__ = "http://bitbucket.org/runeh/anyjson/"
__docformat__ = "restructuredtext"

"""

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

implementation = None

"""
.. data:: _modules

    List of known json modules, and the names of their serialize/unserialize
    methods, as well as the exception they throw. Exception can be either
    an exception class or a string.
"""
_modules = [("cjson", "encode", "EncodeError", "decode", "DecodeError"),
            ("jsonlib2", "write", "WriteError", "read", "ReadError"),
            ("jsonlib", "write", "WriteError", "read", "ReadError"),
            ("simplejson", "dumps", TypeError, "loads", ValueError),
            ("json", "dumps", TypeError, "loads", ValueError),
            ("django.utils.simplejson", "dumps", TypeError, "loads",
             ValueError)]
_fields = ("modname", "encoder", "encerror", "decoder", "decerror")


class _JsonImplementation(object):
    """Incapsulates a JSON implementation"""

    def __init__(self, modspec):
        modinfo = dict(zip(_fields, modspec))

        # No try block. We want importerror to end up at caller
        module = self._attempt_load(modinfo["modname"])

        self.implementation = modinfo["modname"]
        self._encode = getattr(module, modinfo["encoder"])
        self._decode = getattr(module, modinfo["decoder"])
        self._encode_error = modinfo["encerror"]
        self._decode_error = modinfo["decerror"]

        if isinstance(modinfo["encerror"], basestring):
            self._encode_error = getattr(module, modinfo["encerror"])
        if isinstance(modinfo["decerror"], basestring):
            self._decode_error = getattr(module, modinfo["decerror"])

        self.name = modinfo["modname"]

    def _attempt_load(self, modname):
        """Attempt to load module name modname, returning it on success,
        throwing ImportError if module couldn't be imported"""
        __import__(modname)
        return sys.modules[modname]

    def serialize(self, data):
        """Serialize the datastructure to json. Returns a string. Raises
        TypeError if the object could not be serialized."""
        try:
            return self._encode(data)
        except self._encode_error, exc:
            raise TypeError(*exc.args)

    def deserialize(self, s):
        """deserialize the string to python data types. Raises
        ValueError if the string vould not be parsed."""
        try:
            return self._decode(s)
        except self._decode_error, exc:
            raise ValueError(*exc.args)


def force_implementation(modname):
    """Forces anyjson to use a specific json module if it's available"""
    global implementation
    for name, spec in [(e[0], e) for e in _modules]:
        if name == modname:
            implementation = _JsonImplementation(spec)
            return
    raise ImportError("No module named: %s" % modname)


for modspec in _modules:
    try:
        implementation = _JsonImplementation(modspec)
        break
    except ImportError:
        pass
else:
    raise ImportError("No supported JSON module found")

serialize = lambda value: implementation.serialize(value)
deserialize = lambda value: implementation.deserialize(value)
