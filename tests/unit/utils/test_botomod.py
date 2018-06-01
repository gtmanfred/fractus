# -*- coding: utf-8 -*-

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals
import os

# Import Salt libs
from salt.ext import six
from salt.exceptions import SaltInvocationError

# Import Fractus Libs
import fractus.cloudutils.botomod as botomod
import fractus.cloudutils.boto3mod as boto3mod

# Import Testing Libs
import pytest
from mock import MagicMock, patch

boto = pytest.importorskip('boto', minversion='2.0.0')
boto3 = pytest.importorskip('boto3', minversion='1.2.1')
moto = pytest.importorskip('moto')
exception = pytest.importorskip('boto.exception')

service = 'ec2'
resource_name = 'test-instance'
resource_id = 'i-a1b2c3'


error_body = '''
<Response>
    <Errors>
         <Error>
           <Code>Error code text</Code>
           <Message>Error message</Message>
         </Error>
    </Errors>
    <RequestID>request ID</RequestID>
</Response>
'''

no_error_body = '''
<Response>
    <Errors />
    <RequestID>request ID</RequestID>
</Response>
'''


def setup_module():
    module_globals = {
        '__salt__': {'config.get': MagicMock(return_value='dummy_opt')}
    }
    pytest.helpers.setup_loader({botomod: module_globals, boto3mod: module_globals})


def test_set_and_get_with_no_auth_params():
    botomod.cache_id(service, resource_name, resource_id=resource_id)
    assert botomod.cache_id(service, resource_name) == resource_id

def test_set_and_get_with_explicit_auth_params():
    botomod.cache_id(service, resource_name, resource_id=resource_id, **pytest.conn_parameters)
    assert botomod.cache_id(service, resource_name, **pytest.conn_parameters) == resource_id

def test_set_and_get_with_different_region_returns_none():
    botomod.cache_id(service, resource_name, resource_id=resource_id, region='us-east-1')
    assert botomod.cache_id(service, resource_name, region='us-west-2') == None

def test_set_and_get_after_invalidation_returns_none():
    botomod.cache_id(service, resource_name, resource_id=resource_id)
    botomod.cache_id(service, resource_name, resource_id=resource_id, invalidate=True)
    assert botomod.cache_id(service, resource_name) == None

def test_partial():
    cache_id = botomod.cache_id_func(service)
    cache_id(resource_name, resource_id=resource_id)
    assert cache_id(resource_name) == resource_id

@moto.mock_ec2
def test_conn_is_cached():
    conn = botomod.get_connection(service, **pytest.conn_parameters)
    assert conn in botomod.__context__.values()

@moto.mock_ec2
def test_conn_is_cache_with_profile():
    conn = botomod.get_connection(service, profile=pytest.conn_parameters)
    assert conn in botomod.__context__.values()

@moto.mock_ec2
def test_get_conn_with_no_auth_params_raises_invocation_error():
    with patch('boto.{0}.connect_to_region'.format(service),
               side_effect=boto.exception.NoAuthHandlerFound()):
        with pytest.raises(SaltInvocationError):
            botomod.get_connection(service)

@moto.mock_ec2
def test_get_conn_error_raises_command_execution_error():
    with patch('boto.{0}.connect_to_region'.format(service),
               side_effect=exception.BotoServerError(400, 'Mocked error', body=error_body)):
        with pytest.raises(exception.BotoServerError):
            botomod.get_connection(service)

@moto.mock_ec2
def test_partial():
    get_conn = botomod.get_connection_func(service)
    conn = get_conn(**pytest.conn_parameters)
    assert conn in botomod.__context__.values()


def test_error_message():
    e = exception.BotoServerError('400', 'Mocked error', body=error_body)
    r = botomod.get_error(e)
    expected = {'aws': {'code': 'Error code text',
                        'message': 'Error message',
                        'reason': 'Mocked error',
                        'status': '400'},
                'message': 'Mocked error: Error message'}
    assert r == expected

def test_exception_message_with_no_body():
    e = exception.BotoServerError('400', 'Mocked error')
    r = botomod.get_error(e)
    expected = {'aws': {'reason': 'Mocked error',
                        'status': '400'},
                'message': 'Mocked error'}
    assert r == expected

def test_exception_message_with_no_error_in_body():
    e = exception.BotoServerError('400', 'Mocked error', body=no_error_body)
    r = botomod.get_error(e)
    expected = {'aws': {'reason': 'Mocked error', 'status': '400'},
                        'message': 'Mocked error'}
    assert r == expected


def test_context_conflict_between_boto_and_boto3_utils():
    botomod.assign_funcs(__name__, 'ec2')
    boto3mod.assign_funcs(__name__, 'ec2', get_conn_funcname="_get_conn3")

    boto_ec2_conn = botomod.get_connection('ec2',
                                                   region=pytest.region,
                                                   key=pytest.secret_key,
                                                   keyid=pytest.access_key)
    boto3_ec2_conn = boto3mod.get_connection('ec2',
                                                     region=pytest.region,
                                                     key=pytest.secret_key,
                                                     keyid=pytest.access_key)

    # These should *not* be the same object!
    assert id(boto_ec2_conn) != id(boto3_ec2_conn)
