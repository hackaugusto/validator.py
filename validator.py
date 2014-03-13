# -*- coding: utf8 -*-
import sys
import inspect
from math import sqrt, ceil
from enum import Enum
from functools import wraps, partial

try:
    from UserList import UserList
except:
    from collections import UserList

if sys.version[0] == 2:
    from itertools import xrange as range


# We cannot use keywords as identifiers (and, or, xor, assert), lets use some
# constants instead
connective = Enum('AND', 'OR', 'XOR')
AND = connective.AND
OR = connective.OR
XOR = connective.XOR


def chain(validator, function):
    argspec = inspect.getargspec(function)

    if len(argspec.args) == 1:
        return validator & function

    @wraps(function)
    def wrapper(*args, **kwargs):
        # we need to collect the validator arguments
        # using wraps in a partial object does not change its repr, using a lambda to be nicier
        return validator & wraps(function)(lambda value: partial(function, *args, **kwargs)(value))
    return wrapper


def validator(function):
    ''' Lets keep a nice name for the functions '''
    argspec = inspect.getargspec(function)

    if len(argspec.args) == 1:
        @property
        @wraps(function)
        def wrapper(self):
            return self & function
        return wrapper

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        # we need to collect the validator arguments
        # using wraps in a partial object does not change its repr, using a lambda to be nicier
        return self & wraps(function)(lambda value: partial(function, *args, **kwargs)(value))
    return wrapper


class _registry(type(UserList)):
    def __new__(metaclass, class_name, parents, attributes):
        attributes['_validator_registry'] = dict()
        return type.__new__(metaclass, class_name, parents, attributes)


class Validator(UserList):
    __metaclass__ = _registry

    def __init__(self, initialdata=None, connective=AND):
        super(Validator, self).__init__(initialdata)
        self.connective = connective

    def __getattribute__(self, name):
        registry = object.__getattribute__(self, '_validator_registry')
        klass = object.__getattribute__(self, '__class__')

        if name in registry:
            return chain(self, registry[name])

        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            for cls in klass.__bases__:
                base_registry = getattr(cls, '_validator_registry', None)

                if name in base_registry:
                    return chain(self, base_registry[name])

            raise

    def __call__(self, data):
        generator = (callback(data) for callback in self)

        if self.connective == AND:
            return all(generator)

        if self.connective == OR:
            return any(generator)

        if self.connective == XOR:
            # all predicates are false, the setence is false
            if any(generator) is False:
                return False

            # more than one predicate is true, the setence is false
            if any(generator) is True:
                return False

            # only one predicate was true, the sentence is true
            return True

    def register(self, name, validator):
        validator.__name__ = name
        self._validator_registry[name] = validator

    def add(self, callback, connective):
        # changes to self and callback should not change the behavior, so we
        # copy the current state
        newself = self.copy()

        if hasattr(callback, 'copy'):
            newcallback = callback.copy()
        else:
            newcallback = callback

        # these will keep the callback list shallow
        if len(newself) in (0, 1):
            newself.connective = connective

        if newself.connective == connective:
            newself.append(newcallback)
            return newself

        return self.__class__([newself, newcallback], connective)

    def assert_value(self, value, message=None):
        if not self(value):
            raise AssertionError(message)

    def copy(self):
        return self.__class__(self, self.connective)

    def __and__(self, other):
        return self.add(other, AND)

    def __or__(self, other):
        return self.add(other, OR)

    def __xor__(self, other):
        return self.add(other, XOR)

    @validator
    def equals(value, other):
        return value == other

    @validator
    def valuein(possibilities, value):
        return value in possibilities

    @validator
    def instance(checktype, value):
        return isinstance(value, checktype)

    @validator
    def attr(name, value):
        return hasattr(value, name)


class NumberValidator(Validator):
    @validator
    def positive(value):
        return value > 0

    @validator
    def non_positive(value):
        return value <= 0

    @validator
    def negative(value):
        return value < 0

    @validator
    def non_negative(value):
        return value >= 0

    @validator
    def even(value):
        return value % 2 == 0

    @validator
    def odd(value):
        return value % 2 == 1

    @validator
    def perfect_square(value):
        return sqrt(value) * sqrt(value) == value

    @validator
    def integer(value):
        return value.is_integer()

    @validator
    def multiple(factor, value):
        return value % factor

    @validator
    def between(lower, upper, value):
        return lower < value < upper

    @validator
    def open_interval(lower, upper, value):
        return lower < value < upper

    @validator
    def close_interval(lower, upper, value):
        return lower <= value <= upper

    @validator
    def max(upper, value):
        return value < upper

    @validator
    def min(lower, value):
        return lower < value

    @property
    def prime(self):
        def primality(value):
            if value in (0, 1):
                return False

            if value in {2, 3, 5, 7}:
                return True

            if value % 2 == 0:
                return False

            for test in range(3, ceil(sqrt(value)) + 1, 2):
                if value % test == 0:
                    return True

            return False

        return self & primality


class StringValidator(Validator):
    @validator
    def alnum(value):
        return value.isalnum()

    @validator
    def alpha(value):
        return value.isalpha()

    @validator
    def upper(value):
        return value.isupper()

    @validator
    def lower(value):
        return value.islower()

    @validator
    def startswith(prefix, value):
        return value.startswith(prefix)

    @validator
    def endswith(prefix, value):
        return value.endswith(prefix)

    @validator
    def title(value):
        return value.istitle()

    @validator
    def contains(needle, value):
        return needle in value

    @validator
    def digit(value):
        return value.isdigit()

    @validator
    def match(regex, value):
        return regex.match(value)


Number = NumberValidator()
Natural = Number.integer.non_negative
Integer = Number.integer
String = StringValidator()
