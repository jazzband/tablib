# -*- coding: utf-8 -*-

"""
omijson.core
~~~~~~~~~~~~

This module provides the core omnijson functionality.

"""

import sys

engine = None
_engine = None


options = [
    ['ujson', 'loads', 'dumps', (ValueError,)],
    ['yajl', 'loads', 'dumps', (TypeError, ValueError)],
    ['jsonlib2', 'read', 'write', (ValueError,)],
    ['jsonlib', 'read', 'write', (ValueError,)],
    ['simplejson', 'loads', 'dumps', (TypeError, ValueError)],
    ['json', 'loads', 'dumps', (TypeError, ValueError)],
    ['simplejson_from_packages', 'loads', 'dumps', (ValueError,)],
]


def _import(engine):
    try:
        if '_from_' in engine:
            engine, package = engine.split('_from_')
            m = __import__(package, globals(), locals(), [engine], -1)
            return getattr(m, engine)

        return __import__(engine)

    except ImportError:
        return False


def loads(s, **kwargs):
    """Loads JSON object."""

    try:
        return _engine[0](s)

    except:
        # crazy 2/3 exception hack
        # http://www.voidspace.org.uk/python/weblog/arch_d7_2010_03_20.shtml

        ExceptionClass, why = sys.exc_info()[:2]

        if any([(issubclass(ExceptionClass, e)) for e in _engine[2]]):
            raise JSONError(why)
        else:
            raise why


def dumps(o, **kwargs):
    """Dumps JSON object."""

    try:
        return _engine[1](o)

    except:
        ExceptionClass, why = sys.exc_info()[:2]

        if any([(issubclass(ExceptionClass, e)) for e in _engine[2]]):
            raise JSONError(why)
        else:
            raise why


class JSONError(ValueError):
    """JSON Failed."""


# ------
# Magic!
# ------


for e in options:

    __engine = _import(e[0])

    if __engine:
        engine, _engine = e[0], e[1:4]

        for i in (0, 1):
            _engine[i] = getattr(__engine, _engine[i])

        break
