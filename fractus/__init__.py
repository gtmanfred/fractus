# -*- coding: utf-8 -*-
'''
Cloud modules for managing clouds from salt
'''
from __future__ import absolute_import, unicode_literals

# Import python libraries
import os

FRACTUS_BASE_PATH = os.path.dirname(__file__)


def utils_dirs():
    '''
    Cloud utils modules
    '''
    yield os.path.join(FRACTUS_BASE_PATH, 'cloudutils')


def module_dirs():
    '''
    Cloud execution modules
    '''
    yield os.path.join(FRACTUS_BASE_PATH, 'cloudmodules')


def state_dirs():
    '''
    Cloud execution states
    '''
    yield os.path.join(FRACTUS_BASE_PATH, 'cloudstates')


def runner_dirs():
    '''
    Cloud runner modules
    '''
    yield os.path.join(FRACTUS_BASE_PATH, 'cloudmodules')
