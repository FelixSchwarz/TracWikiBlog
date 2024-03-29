# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# I believe the license above is permissible enough so you can actually 
# use/relicense the code in any other project without license proliferation. 
# I'm happy to relicense this code if necessary for inclusion in other free 
# software projects.

# TODO / nice to have
#  - raising assertions (with message building) should be unified
#  - shorted tracebacks for cascaded calls so it's easier to look at the 
#    traceback as a user 
#      see jinja2/debug.py for some code that does such hacks:
#          https://github.com/mitsuhiko/jinja2/blob/master/jinja2/debug.py


__all__ = ['assert_contains', 'assert_equals', 'assert_false', 'assert_length',
           'assert_none', 'assert_not_none', 'assert_not_equals', 
           'assert_raises', 'assert_true', ]


def assert_raises(exception, callable, message=None):
    try:
        callable()
    except exception, e:
        return e
    default_message = u'%s not raised!' % exception.__name__
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ' ' + message)

def assert_equals(expected, actual, message=None):
    if expected == actual:
        return
    default_message = '%s != %s' % (repr(expected), repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_none(actual, message=None):
    assert_equals(None, actual, message=message)

def assert_false(actual, message=None):
    assert_equals(False, actual, message=message)

def assert_true(actual, message=None):
    assert_equals(True, actual, message=message)

def assert_length(expected_length, actual_iterable, message=None):
    assert_equals(expected_length, len(actual_iterable), message=message)

def assert_not_equals(expected, actual, message=None):
    if expected != actual:
        return
    default_message = '%s == %s' % (repr(expected), repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_not_none(actual, message=None):
    assert_not_equals(None, actual, message=message)

def assert_contains(expected_value, actual_iterable, message=None):
    if expected_value in actual_iterable:
        return
    default_message = '%s not in %s' % (repr(expected_value), repr(actual_iterable))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_not_contains(expected_value, actual_iterable, message=None):
    if expected_value not in actual_iterable:
        return
    default_message = '%s in %s' % (repr(expected_value), repr(actual_iterable))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_is_empty(actual, message=None):
    if len(actual) == 0:
        return
    default_message = '%s is not empty' % (repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_is_not_empty(actual, message=None):
    if len(actual) > 0:
        return
    default_message = '%s is empty' % (repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)


# almost_equals
# isinstance
# smaller_than
# greater_than
# is_callable
# falsish, trueish
