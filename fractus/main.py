# -*- coding: utf-8 -*-
'''
Main fractus entry point
'''
from __future__ import absolute_import, unicode_literals

# Import python libraries
import os

# Import salt libraries
import salt.output
import salt.utils.jid
import salt.utils.state

# Import Fractus libraries
import fractus.config
import fractus.parser
import fractus.state

class Runner(object):
    def __init__(self):
        self._prepare_fractus()
        self.opts = fractus.config.fractus_config(conf_file=self.options.config)
        self.opts['test'] = self.options.test
        self.st_ = fractus.state.FractusState(self.opts, jid=salt.utils.jid.gen_jid(self.opts))

    def _prepare_fractus(self):
        self.options = fractus.parser.parse()

    def __call__(self):
        high_, errors = self.st_.render_highstate({'base': self.options.mods})

        if errors:
            return errors, 'nested'

        ret = {'data': {'local': self.st_.state.call_high(high_)}}
        ret['retcode'] = 0 if salt.utils.state.check_result(ret['data']) else 1
        return ret, 'highstate'


def main():
    runner = Runner()
    salt.log.setup.setup_console_logger(runner.options.log_level or runner.opts['log_level'])
    ret, out = runner()
    salt.output.display_output(
        ret,
        out=runner.options.out or out,
        opts=runner.opts,
    )
