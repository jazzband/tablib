from typecheck import Typeclass

### Number
####################################################

_numbers = [int, float, complex, long, bool]
try:
    from decimal import Decimal
    _numbers.append(Decimal)
    del Decimal
except ImportError:
    pass
    
Number = Typeclass(*_numbers)
del _numbers
    
### String -- subinstance of ImSequence
####################################################

String = Typeclass(str, unicode)
    
### ImSequence -- immutable sequences
####################################################

ImSequence = Typeclass(tuple, xrange, String)

### MSequence -- mutable sequences
####################################################

MSequence = Typeclass(list)

### Mapping
####################################################

Mapping = Typeclass(dict)
