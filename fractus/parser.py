# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Import python libraries
import argparse
import xdg


def parse():
    parser = argparse.ArgumentParser(description='Fractus Cloud States Runner')
    parser.add_argument('mods', metavar='state', type=str, nargs='+',
                        help='states to run')
    parser.add_argument('--config', dest='config', type=str, default=None,
                        help='Config file (default {0}/fractus/config.yml'.format(xdg.XDG_CONFIG_HOME))
    parser.add_argument('--test', action='store_true', default=False,
                        help='Test state runs')
    parser.add_argument('--out', '-o', dest='out', type=str, default=None,
                        help='Which outputter to use')
    parser.add_argument('--log-level', '-l', dest='log_level', type=str, default=None,
                        help='set LogLevel')
    return parser.parse_args()
