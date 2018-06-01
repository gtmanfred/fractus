# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Import python libraries
import pytest
import random
import string

# Import salt libraries
import salt.ext.six as six
from salt.ext.six.moves import range

# Import fractus libraries
import fractus.config
import fractus.loader

# Import test libraries
from mock import MagicMock, patch

pytest_plugins = ['helpers_namespace']


pytest.opts = fractus.config.fractus_config()
pytest.utils = fractus.loader.cloudutils(pytest.opts)
pytest.modules = fractus.loader.cloudmodules(pytest.opts, utils=pytest.utils)
pytest.states = fractus.loader.cloudstates(pytest.opts, functions=pytest.modules, utils=pytest.utils)
pytest.region = 'us-east-1'
pytest.access_key = 'GKTADJGHEIQSXMKKRBJ08H'
pytest.secret_key = 'askdjghsdfjkghWupUjasdflkdfklgjsdfjajkghs'
pytest.conn_parameters = {'region': pytest.region, 'key': pytest.access_key, 'keyid': pytest.secret_key, 'profile': {}}


@pytest.helpers.register
def setup_loader(setup):
    defaults = {
        '__salt__',
        '__opts__',
        '__grains__',
        '__utils__',
        '__states__',
        '__serializers__',
        '__context__',
    }

    for mod, opts in six.iteritems(setup):
        for key, val in six.iteritems(opts):
            setattr(mod, key, val)
        for key in defaults - set(opts.keys()):
            setattr(mod, key, {})


@pytest.fixture
def boto_conn():
    # Set up MagicMock to replace the boto3 session
    # connections keep getting cached from prior tests, can't find the
    # correct context object to clear it. So randomize the cache key, to prevent any
    # cache hits
    pytest.conn_parameters['key'] = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(50))

    patcher = patch('boto3.session.Session')
    mock_session = patcher.start()

    session_instance = mock_session.return_value
    conn = MagicMock()
    session_instance.client.return_value = conn

    yield conn

    patcher.stop()
