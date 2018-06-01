# -*- coding: utf-8 -*-
'''
Return config information
'''
from __future__ import absolute_import, unicode_literals

# Import python libraries
import copy
import logging

# Import salt libraries
import salt.utils.dictupdate
import salt.utils.sdb as sdb

try:
    from salt.utils.data import traverse_dict_and_list
except ImportError:
    from salt.utils import traverse_dict_and_list

log = logging.getLogger(__name__)
DEFAULTS = {}


def option(
        value,
        default='',
        omit_opts=False,
        omit_master=False,
        omit_pillar=False):
    '''
    Pass in a generic option and receive the value that will be assigned

    CLI Example:

    .. code-block:: bash

        salt '*' config.option redis.host
    '''
    if not omit_opts:
        if value in __opts__:
            return __opts__[value]
    if not omit_master:
        if value in __pillar__.get('master', {}):
            return __pillar__['master'][value]
    if not omit_pillar:
        if value in __pillar__:
            return __pillar__[value]
    if value in DEFAULTS:
        return DEFAULTS[value]
    return default


def get(key, default='', delimiter=':', merge=None, omit_opts=False,
        omit_pillar=False, omit_master=False, omit_grains=False):
    if merge is None:
        if not omit_opts:
            ret = traverse_dict_and_list(
                __opts__,
                key,
                '_|-',
                delimiter=delimiter)
            if ret != '_|-':
                return sdb.sdb_get(ret, __opts__)

        if not omit_grains:
            ret = traverse_dict_and_list(
                __grains__,
                key,
                '_|-',
                delimiter)
            if ret != '_|-':
                return sdb.sdb_get(ret, __opts__)

        if not omit_pillar:
            ret = traverse_dict_and_list(
                __pillar__,
                key,
                '_|-',
                delimiter=delimiter)
            if ret != '_|-':
                return sdb.sdb_get(ret, __opts__)

        if not omit_master:
            ret = traverse_dict_and_list(
                __pillar__.get('master', {}),
                key,
                '_|-',
                delimiter=delimiter)
            if ret != '_|-':
                return sdb.sdb_get(ret, __opts__)

        ret = traverse_dict_and_list(
            DEFAULTS,
            key,
            '_|-',
            delimiter=delimiter)
        log.debug("key: %s, ret: %s", key, ret)
        if ret != '_|-':
            return sdb.sdb_get(ret, __opts__)
    else:
        if merge not in ('recurse', 'overwrite'):
            log.warning('Unsupported merge strategy \'{0}\'. Falling back '
                        'to \'recurse\'.'.format(merge))
            merge = 'recurse'

        data = copy.copy(DEFAULTS)
        data = salt.utils.dictupdate.merge(data, __pillar__.get('master', {}), strategy=merge)
        data = salt.utils.dictupdate.merge(data, __pillar__, strategy=merge)
        data = salt.utils.dictupdate.merge(data, __grains__, strategy=merge)
        data = salt.utils.dictupdate.merge(data, __opts__, strategy=merge)
        ret = traverse_dict_and_list(
            data,
            key,
            '_|-',
            delimiter=delimiter)
        if ret != '_|-':
            return sdb.sdb_get(ret, __opts__)

    return default
