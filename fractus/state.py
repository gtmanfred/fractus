# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Import Python Libraries
import logging

# Import Salt Libraries
import salt.state
import salt.loader

# Import Fractus Libraries
import fractus.loader

log = logging.getLogger(__name__)


class FractusState(salt.state.HighState):
    def load_modules(self, data=None, proxy=None):
        '''
        Load the modules into the state
        '''
        log.info('Loading fresh modules for state activity')
        self.utils = fractus.loader.utils(self.opts)
        self.functions = fractus.loader.cloudmodules(self.opts, self.state_con, utils=self.utils)
        self.serializers = salt.loader.serializers(self.opts)
        self.states = fractus.loader.cloudstates(self.opts, self.functions, self.utils)

        self.rend = salt.loader.render(self.opts, self.functions, states=self.states, proxy=self.proxy)
