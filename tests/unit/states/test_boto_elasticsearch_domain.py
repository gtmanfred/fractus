# -*- coding: utf-8 -*-
# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging
import random
import string

# Import Salt libs
from salt.ext import six
import salt.loader

# Import Fractus Libs
import fractus.cloudstates.boto_elasticsearch_domain as boto_elasticsearch_domain

# Import Testing libs
import pytest
pytestmark = pytest.mark.skip('all tests still WIP')


# the boto_elasticsearch_domain module relies on the connect_to_region() method
# which was added in boto 2.8.0
# https://github.com/boto/boto/commit/33ac26b416fbb48a60602542b4ce15dcc7029f12
required_boto3_version = '1.2.1'

log = logging.getLogger(__name__)


def setup_loader_modules(self):
    ctx = {}
    utils = salt.loader.utils(self.opts, whitelist=['boto3'], context=ctx)
    serializers = salt.loader.serializers(self.opts)
    self.funcs = funcs = salt.loader.minion_mods(self.opts, context=ctx, utils=utils, whitelist=['boto_elasticsearch_domain'])
    self.salt_states = salt.loader.states(opts=self.opts, functions=funcs, utils=utils, whitelist=['boto_elasticsearch_domain'],
                                          serializers=serializers)
    return {
        boto_elasticsearch_domain: {
            '__opts__': self.opts,
            '__salt__': funcs,
            '__utils__': utils,
            '__states__': self.salt_states,
            '__serializers__': serializers,
        }
    }


def test_present_when_domain_does_not_exist():
    '''
    Tests present on a domain that does not exist.
    '''
    self.conn.describe_elasticsearch_domain.side_effect = not_found_error
    self.conn.describe_elasticsearch_domain_config.return_value = {'DomainConfig': domain_ret}
    self.conn.create_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = self.salt_states['boto_elasticsearch_domain.present'](
                     'domain present',
                     **domain_ret)

    self.assertTrue(result['result'])
    self.assertEqual(result['changes']['new']['domain']['ElasticsearchClusterConfig'], None)

def test_present_when_domain_exists():
    self.conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    cfg = {}
    for k, v in six.iteritems(domain_ret):
        cfg[k] = {'Options': v}
    cfg['AccessPolicies'] = {'Options': '{"a": "b"}'}
    self.conn.describe_elasticsearch_domain_config.return_value = {'DomainConfig': cfg}
    self.conn.update_elasticsearch_domain_config.return_value = {'DomainConfig': cfg}
    result = self.salt_states['boto_elasticsearch_domain.present'](
                     'domain present',
                     **domain_ret)
    self.assertTrue(result['result'])
    self.assertEqual(result['changes'], {'new': {'AccessPolicies': {}}, 'old': {'AccessPolicies': {'a': 'b'}}})

def test_present_with_failure():
    self.conn.describe_elasticsearch_domain.side_effect = not_found_error
    self.conn.describe_elasticsearch_domain_config.return_value = {'DomainConfig': domain_ret}
    self.conn.create_elasticsearch_domain.side_effect = ClientError(error_content, 'create_domain')
    result = self.salt_states['boto_elasticsearch_domain.present'](
                     'domain present',
                     **domain_ret)
    self.assertFalse(result['result'])
    self.assertTrue('An error occurred' in result['comment'])

def test_absent_when_domain_does_not_exist():
    '''
    Tests absent on a domain that does not exist.
    '''
    self.conn.describe_elasticsearch_domain.side_effect = not_found_error
    result = self.salt_states['boto_elasticsearch_domain.absent']('test', 'mydomain')
    self.assertTrue(result['result'])
    self.assertEqual(result['changes'], {})

def test_absent_when_domain_exists():
    self.conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    self.conn.describe_elasticsearch_domain_config.return_value = {'DomainConfig': domain_ret}
    result = self.salt_states['boto_elasticsearch_domain.absent']('test', domain_ret['DomainName'])
    self.assertTrue(result['result'])
    self.assertEqual(result['changes']['new']['domain'], None)

def test_absent_with_failure():
    self.conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    self.conn.describe_elasticsearch_domain_config.return_value = {'DomainConfig': domain_ret}
    self.conn.delete_elasticsearch_domain.side_effect = ClientError(error_content, 'delete_domain')
    result = self.salt_states['boto_elasticsearch_domain.absent']('test', domain_ret['DomainName'])
    self.assertFalse(result['result'])
    self.assertTrue('An error occurred' in result['comment'])
