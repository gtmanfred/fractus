# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import copy
import logging
import random
import string

# Import Salt libs
from salt.ext import six

# Import Fractus Libs
import fractus.cloudmodules.boto_elasticsearch_domain as boto_elasticsearch_domain

# Import Testing libs
import pytest
from mock import MagicMock, patch


boto3 = pytest.importorskip('boto3', minversion='1.2.1')
exceptions = pytest.importorskip('botocore.exceptions')


error_message = 'An error occurred (101) when calling the {0} operation: Test-defined error'
error_content = {
  'Error': {
    'Code': 101,
    'Message': "Test-defined error"
  }
}
not_found_error = exceptions.ClientError({
    'Error': {
        'Code': 'ResourceNotFoundException',
        'Message': "Test-defined error"
    }
}, 'msg')
domain_ret = dict(DomainName='testdomain',
                  ElasticsearchClusterConfig={},
                  EBSOptions={},
                  AccessPolicies={},
                  SnapshotOptions={},
                  AdvancedOptions={})

log = logging.getLogger(__name__)


def setup_module():
    pytest.helpers.setup_loader({
        boto_elasticsearch_domain: {
            '__utils__': pytest.utils,
        },
    })
    boto_elasticsearch_domain.__init__(pytest.opts)


@pytest.mark.xfail
def test_that_when_checking_if_a_domain_exists_and_a_domain_exists_the_domain_exists_method_returns_true():
    '''
    Tests checking domain existence when the domain already exists
    '''
    result = boto_elasticsearch_domain.exists(DomainName='testdomain', **pytest.conn_parameters)

    assert result['exists'] is True

def test_that_when_checking_if_a_domain_exists_and_a_domain_does_not_exist_the_domain_exists_method_returns_false(boto_conn):
    '''
    Tests checking domain existence when the domain does not exist
    '''
    boto_conn.describe_elasticsearch_domain.side_effect = not_found_error
    result = boto_elasticsearch_domain.exists(DomainName='mydomain', **pytest.conn_parameters)

    assert result['exists'] is False

def test_that_when_checking_if_a_domain_exists_and_boto3_returns_an_error_the_domain_exists_method_returns_error(boto_conn):
    '''
    Tests checking domain existence when boto returns an error
    '''
    boto_conn.describe_elasticsearch_domain.side_effect = exceptions.ClientError(error_content, 'list_domains')
    result = boto_elasticsearch_domain.exists(DomainName='mydomain', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('list_domains')

def test_that_when_checking_domain_status_and_a_domain_exists_the_domain_status_method_returns_info(boto_conn):
    '''
    Tests checking domain existence when the domain already exists
    '''
    boto_conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = boto_elasticsearch_domain.status(DomainName='testdomain', **pytest.conn_parameters)

    assert result['domain']

def test_that_when_checking_domain_status_and_boto3_returns_an_error_the_domain_status_method_returns_error(boto_conn):
    '''
    Tests checking domain existence when boto returns an error
    '''
    boto_conn.describe_elasticsearch_domain.side_effect = exceptions.ClientError(error_content, 'list_domains')
    result = boto_elasticsearch_domain.status(DomainName='mydomain', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('list_domains')

def test_that_when_describing_domain_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if domain exists
    '''
    domainconfig = {}
    for k, v in six.iteritems(domain_ret):
        if k == 'DomainName':
            continue
        domainconfig[k] = {'Options': v}
    boto_conn.describe_elasticsearch_domain_config.return_value = {'DomainConfig': domainconfig}

    result = boto_elasticsearch_domain.describe(DomainName=domain_ret['DomainName'], **pytest.conn_parameters)

    desired_ret = copy.copy(domain_ret)
    desired_ret.pop('DomainName')
    assert result == {'domain': desired_ret}

def test_that_when_describing_domain_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.describe_elasticsearch_domain_config.side_effect = exceptions.ClientError(error_content, 'list_domains')
    result = boto_elasticsearch_domain.describe(DomainName='testdomain', **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_creating_a_domain_succeeds_the_create_domain_method_returns_true(boto_conn):
    '''
    tests True domain created.
    '''
    boto_conn.create_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    args = copy.copy(domain_ret)
    args.update(pytest.conn_parameters)
    result = boto_elasticsearch_domain.create(**args)

    assert result['created'] is True

def test_that_when_creating_a_domain_fails_the_create_domain_method_returns_error(boto_conn):
    '''
    tests False domain not created.
    '''
    boto_conn.create_elasticsearch_domain.side_effect = exceptions.ClientError(error_content, 'create_domain')
    args = copy.copy(domain_ret)
    args.update(pytest.conn_parameters)
    result = boto_elasticsearch_domain.create(**args)
    assert result.get('error', {}).get('message') == error_message.format('create_domain')

def test_that_when_deleting_a_domain_succeeds_the_delete_domain_method_returns_true():
    '''
    tests True domain deleted.
    '''
    result = boto_elasticsearch_domain.delete(DomainName='testdomain', **pytest.conn_parameters)
    assert result['deleted'] is True

def test_that_when_deleting_a_domain_fails_the_delete_domain_method_returns_false(boto_conn):
    '''
    tests False domain not deleted.
    '''
    boto_conn.delete_elasticsearch_domain.side_effect = exceptions.ClientError(error_content, 'delete_domain')
    result = boto_elasticsearch_domain.delete(DomainName='testdomain',
                                                **pytest.conn_parameters)
    assert result['deleted'] is False

def test_that_when_updating_a_domain_succeeds_the_update_domain_method_returns_true(boto_conn):
    '''
    tests True domain updated.
    '''
    boto_conn.update_elasticsearch_domain_config.return_value = {'DomainConfig': domain_ret}
    args = copy.copy(domain_ret)
    args.update(pytest.conn_parameters)
    result = boto_elasticsearch_domain.update(**args)

    assert result['updated'] is True

def test_that_when_updating_a_domain_fails_the_update_domain_method_returns_error(boto_conn):
    '''
    tests False domain not updated.
    '''
    boto_conn.update_elasticsearch_domain_config.side_effect = exceptions.ClientError(error_content, 'update_domain')
    args = copy.copy(domain_ret)
    args.update(pytest.conn_parameters)
    result = boto_elasticsearch_domain.update(**args)
    assert result.get('error', {}).get('message') ==  error_message.format('update_domain')

def test_that_when_adding_tags_succeeds_the_add_tags_method_returns_true(boto_conn):
    '''
    tests True tags added.
    '''
    boto_conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = boto_elasticsearch_domain.add_tags(DomainName='testdomain', a='b', **pytest.conn_parameters)

    assert result['tagged'] is True

def test_that_when_adding_tags_fails_the_add_tags_method_returns_false(boto_conn):
    '''
    tests False tags not added.
    '''
    boto_conn.add_tags.side_effect = exceptions.ClientError(error_content, 'add_tags')
    boto_conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = boto_elasticsearch_domain.add_tags(DomainName=domain_ret['DomainName'], a='b', **pytest.conn_parameters)
    assert result['tagged'] is False

def test_that_when_removing_tags_succeeds_the_remove_tags_method_returns_true(boto_conn):
    '''
    tests True tags removed.
    '''
    boto_conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = boto_elasticsearch_domain.remove_tags(DomainName=domain_ret['DomainName'], TagKeys=['a'], **pytest.conn_parameters)

    assert result['tagged'] is True

def test_that_when_removing_tags_fails_the_remove_tags_method_returns_false(boto_conn):
    '''
    tests False tags not removed.
    '''
    boto_conn.remove_tags.side_effect = exceptions.ClientError(error_content, 'remove_tags')
    boto_conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = boto_elasticsearch_domain.remove_tags(DomainName=domain_ret['DomainName'], TagKeys=['b'], **pytest.conn_parameters)
    assert result['tagged'] is False

def test_that_when_listing_tags_succeeds_the_list_tags_method_returns_true(boto_conn):
    '''
    tests True tags listed.
    '''
    boto_conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = boto_elasticsearch_domain.list_tags(DomainName=domain_ret['DomainName'], **pytest.conn_parameters)

    assert result['tags'] == {}

def test_that_when_listing_tags_fails_the_list_tags_method_returns_false(boto_conn):
    '''
    tests False tags not listed.
    '''
    boto_conn.list_tags.side_effect = exceptions.ClientError(error_content, 'list_tags')
    boto_conn.describe_elasticsearch_domain.return_value = {'DomainStatus': domain_ret}
    result = boto_elasticsearch_domain.list_tags(DomainName=domain_ret['DomainName'], **pytest.conn_parameters)
    assert result['error']
