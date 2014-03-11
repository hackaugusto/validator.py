# -*- coding: utf8 -*-
import sys

from math import sqrt, ceil
from enum import Enum
from functools import wraps

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


def validator(function):
    ''' Lets keep a nice name for the functions '''
    @property
    def wrapper(self):
        return self & function
    return wrapper


class Validator(UserList):
    def __init__(self, initialdata=None, connective=AND):
        super(Validator, self).__init__(initialdata)
        self.connective = connective

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
        return self.__class__(self)

    def __and__(self, other):
        return self.add(other, AND)

    def __or__(self, other):
        return self.add(other, OR)

    def __xor__(self, other):
        return self.add(other, XOR)

    def equals(self, value):
        return self & (lambda other: value == other)


class NumberValidator(Validator):
    @validator
    def positive(value):
        return value > 0

    @validator
    def negative(value):
        return value < 0

    @validator
    def even(value):
        return value % 2 == 0

    # This approach preserver the validator name, can be useful as some sort of metadata
    @validator
    def odd(value):
        return value % 2 == 1

    # This approach gives no metadata whatsoever
    @property
    def perfectSquare(self):
        return self & (lambda value: sqrt(value) * sqrt(value) == value)

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

    def between(self, lower, upper):
        return self & (lambda value: lower < value < upper)

    def multiple(self, factor):
        return self & (lambda value: value % factor)

# TODO: try it with staticmethod's
Number = NumberValidator()
