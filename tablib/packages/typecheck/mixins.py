from typecheck import _TC_NestedError, _TC_TypeError, check_type, Or
from typecheck import register_type, _TC_Exception

class _TC_IterationError(_TC_NestedError):
    def __init__(self, iteration, value, inner_exception):
        _TC_NestedError.__init__(self, inner_exception)
    
        self.iteration = iteration
        self.value = value
        
    def error_message(self):
        return ("at iteration %d (value: %s)" % (self.iteration, repr(self.value))) + _TC_NestedError.error_message(self)

### This is the shadow class behind UnorderedIteratorMixin.
### Again, it tries to pretend it doesn't exist by mimicing
### the class of <obj> as much as possible.
###
### This mixin provides typechecking for iterator classes
### where you don't care about the order of the types (ie,
### you simply Or() the types together, as opposed to patterned
### lists, which would be ordered mixins)
class _UnorderedIteratorMixin(object):
    def __init__(self, class_name, obj):
        vals = [o for o in obj]
    
        self.type = self
        self._type = Or(*vals)
        self.__cls = obj.__class__
        self.__vals = vals
        # This is necessary because it's a huge pain in the ass
        # to get the "raw" name of the class once it's created
        self.__cls_name = class_name

    def __typecheck__(self, func, to_check):
        if not isinstance(to_check, self.__cls):
            raise _TC_TypeError(to_check, self)

        for i, item in enumerate(to_check):
            try:
                check_type(self._type, func, item)
            except _TC_Exception, e:
                raise _TC_IterationError(i, item, e)

    @classmethod    
    def __typesig__(cls, obj):
        if isinstance(obj, cls):
            return obj

    def __str__(self):
        return "%s(%s)" % (self.__cls_name, str(self._type))

    __repr__ = __str__

### This is included in a class's parent-class section like so:
###  class MyClass(UnorderedIteratorMixin("MyClass")):
###    blah blah blah
###
### This serves as a class factory, whose produced classes
### attempt to mask the fact they exist. Their purpose
### is to redirect __typesig__ calls to appropriate
### instances of _UnorderedIteratorMixin
def UnorderedIteratorMixin(class_name):
    class UIM(object):
        @classmethod
        def __typesig__(cls, obj):
            if isinstance(obj, cls):
                return _UnorderedIteratorMixin(class_name, obj)

        def __repr__(self):
            return "%s%s" % (class_name, str(tuple(e for e in self)))

    # We register each produced class anew
    # If someone needs to unregister these classes, they should
    # save a copy of it before including it in the class-definition:
    #
    # my_UIM = UnorderedIteratorMixin("FooClass")
    # class FooClass(my_UIM):
    #   ...
    #
    # Alternatively, you could just look in FooClass.__bases__ later; whatever
    register_type(UIM)
    return UIM
    
register_type(_UnorderedIteratorMixin)
