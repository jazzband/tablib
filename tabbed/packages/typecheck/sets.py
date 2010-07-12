from typecheck import CheckType, _TC_TypeError, check_type, Type
from typecheck import register_type, Or, _TC_Exception, _TC_KeyError
from typecheck import _TC_LengthError

### Provide typechecking for the built-in set() class
###
### XXX: Investigate rewriting this in terms of
### UnorderedIteratorMixin or Or()          
class Set(CheckType):
    def __init__(self, set_list):
        self.type = set(set_list)
        self._types = [Type(t) for t in self.type]
        
        # self._type is used to build _TC_TypeError
        if len(self._types) > 1:
            self._type = Or(*self.type)
        elif len(self._types) == 1:
            # XXX Is there an easier way to get this?
            t = self.type.pop()
            self._type = t
            self.type.add(t)
    
    def __str__(self):
        return "Set(" + str([e for e in self.type]) + ")"
        
    __repr__ = __str__
    
    def __typecheck__(self, func, to_check):
        if not isinstance(to_check, set):
            raise _TC_TypeError(to_check, self.type)
            
        if len(self._types) == 0 and len(to_check) > 0:
            raise _TC_LengthError(len(to_check), 0)
            
        for obj in to_check:
            error = False
            for type in self._types:
                try:
                    check_type(type, func, obj)
                except _TC_Exception:
                    error = True
                    continue
                else:
                    error = False
                    break
            if error:
                raise _TC_KeyError(obj, _TC_TypeError(obj, self._type))

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self.type == other.type
        
    def __hash__(self):
        return hash(str(hash(self.__class__)) + str(hash(frozenset(self.type))))
            
    @classmethod
    def __typesig__(self, obj):
        if isinstance(obj, set):
            return Set(obj)

register_type(Set)
