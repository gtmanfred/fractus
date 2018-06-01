# -*- coding: utf-8 -*-
'''
Utils for Fractus internals
'''
from __future__ import absolute_import, unicode_literals


# Import Python libs
import types

# Import Salt libs
try:
    from salt.utils.functools import namespaced_function
except ImportError:
    from salt.utils import namespaced_function
