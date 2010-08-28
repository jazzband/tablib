"""
This module allows doctest to find typechecked functions.

Currently, doctest verifies functions to make sure that their
globals() dict is the __dict__ of their module. In the case of
decorated functions, the globals() dict *is* not the right one.

To enable support for doctest do:
    
    import typecheck.doctest_support

This import must occur before any calls to doctest methods.
"""

def __DocTestFinder_from_module(self, module, object):
    """
    Return true if the given object is defined in the given
    module.
    """
    import inspect
    
    if module is None:
        return True 
    elif inspect.isfunction(object) or inspect.isclass(object):
        return module.__name__ == object.__module__
    elif inspect.getmodule(object) is not None:
        return module is inspect.getmodule(object)
    elif hasattr(object, '__module__'):
        return module.__name__ == object.__module__
    elif isinstance(object, property):
        return True # [XX] no way not be sure.
    else:
        raise ValueError("object must be a class or function")

import doctest as __doctest
__doctest.DocTestFinder._from_module = __DocTestFinder_from_module