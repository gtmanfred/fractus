# -*- coding: utf-8 -*-
'''
Loader for Fractus cloud modules
'''
from __future__ import absolute_import, unicode_literals

# Import python libraries
import os

# Import Salt libraries
import salt.loader

# Import Fractus libraries
import fractus


def cloudutils(opts, context=None):
    '''
    Returns the cloud utility modules
    '''
    moddirs = salt.loader._module_dirs(opts, 'cloudutils', 'cloudutils', base_path=fractus.FRACTUS_BASE_PATH)
    moddirs.extend(salt.loader._module_dirs(opts, 'helpers', 'helpers', base_path=fractus.FRACTUS_BASE_PATH))
    return salt.loader.LazyLoader(
        moddirs,
        opts,
        tag='cloudutils',
        pack={'__context__': context},
    )


def cloudmodules(opts, utils=None, context=None):
    '''
    Returns the cloud execution modules
    '''
    if utils is None:
        utils = cloudutils(opts)
    moddirs = salt.loader._module_dirs(opts, 'cloudmodules', 'cloudmodules', base_path=fractus.FRACTUS_BASE_PATH)
    moddirs.extend(salt.loader._module_dirs(opts, 'helpers', 'helpers', base_path=fractus.FRACTUS_BASE_PATH))
    ret = salt.loader.LazyLoader(
        moddirs,
        opts,
        tag='cloudmodules',
        pack={'__context__': context, '__utils__': utils},
    )
    ret.pack['__salt__'] = ret
    return ret


def cloudstates(opts, functions=None, utils=None, context=None):
    '''
    Returns the cloud execution modules
    '''
    if functions is None:
        functions = cloudmodules(opts, utils=utils)
        utils = functions.pack['__utils__']
    if utils is None:
        utils = cloudutils(opts)
        functions.pack['__utils__'] = utils
    ret = salt.loader.LazyLoader(
        salt.loader._module_dirs(opts, 'cloudstates', 'cloudstates', base_path=fractus.FRACTUS_BASE_PATH),
        opts,
        tag='cloudstates',
        pack={'__context__': context, '__utils__': utils, '__salt__': functions},
    )
    ret.pack['__states__'] = ret
    return ret
