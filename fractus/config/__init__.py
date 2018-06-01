# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Import python libraries
import os
import xdg

# Import salt libraries
import salt.config
import salt.ext.six as six

# Import Fractus libraries
import fractus.utils

VALID_OPTS = {
    'extension_modules': six.string_types,
    'file_root': six.string_types,
    'file_ignore_regex': (list, six.string_types),
    'file_ignore_glob': (list, six.string_types),
    'renderer': six.string_types,
    'log_level': six.string_types,
}

DEFAULTS = {
    'extension_modules': '{0}/fractus/extmods'.format(xdg.XDG_CACHE_HOME),
    'file_root': os.getcwd(),
    'file_ignore_regex': [],
    'file_ignore_glob': [],
    'renderer': 'yaml_jinja',
    'log_level': 'warning',
}


_validate_opts = fractus.utils.namespaced_function(salt.config._validate_opts, globals())


def fractus_config(conf_file=None, env_var='FRACTUS_CONFIG'):
    if conf_file is None:
        conf_file = '{0}/fractus/config.yml'.format(xdg.XDG_CONFIG_HOME)
    opts = salt.utils.dictupdate.merge(salt.config.load_config(conf_file, env_var), DEFAULTS)
    opts.update({
        'file_client': 'local',
        'fileserver_backend': ['roots'],
        'cachedir': '{0}/fractus'.format(xdg.XDG_CACHE_HOME),
        'file_roots': {
            'base': [opts.pop('file_root')]
        },
        'state_top': 'salt://top.sls',
        'state_auto_order': True,
        'fileserver_followsymlinks': True,
        'fileserver_ignoresymlinks': False,
        'id': 'local',
        'saltenv': 'base',
        'pillar_cache': False,
        'pillar_roots': {},
        'renderer_blacklist': [],
        'renderer_whitelist': [],
        'hash_type': 'sha256',
        'file_buffer_size': 262144,
    })

    salt.config.apply_sdb(opts)
    _validate_opts(opts)

    opts['__role'] = 'fractus'

    return opts
