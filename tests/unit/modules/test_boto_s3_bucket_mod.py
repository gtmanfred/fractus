# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging
from copy import deepcopy

# Import Salt libs
from salt.ext import six

# Import Fractus Libs
import salt.modules.boto_s3_bucket as boto_s3_bucket

# Import Testing Libs
import pytest

boto = pytest.importorskip('boto')
boto3 = pytest.importorskip('boto3')
exceptions = pytest.importorskip('botocore.exceptions')

log = logging.getLogger(__name__)

error_message = 'An error occurred (101) when calling the {0} operation: Test-defined error'
e404_error = exceptions.ClientError({
    'Error': {
        'Code': '404',
        'Message': "Test-defined error"
    }
}, 'msg')
not_found_error = exceptions.ClientError({
    'Error': {
        'Code': 'NoSuchBucket',
        'Message': "Test-defined error"
    }
}, 'msg')
error_content = {
  'Error': {
    'Code': 101,
    'Message': "Test-defined error"
  }
}
create_ret = {
    'Location': 'nowhere',
}
list_ret = {
    'Buckets': [{
        'Name': 'mybucket',
        'CreationDate': None
    }],
    'Owner': {
        'DisplayName': 'testuser',
        'ID': '12341234123'
    },
    'ResponseMetadata': {'Key': 'Value'}
}
config_ret = {
    'get_bucket_acl': {
        'Grants': [{
            'Grantee': {
                'DisplayName': 'testowner',
                'ID': 'sdfghjklqwertyuiopzxcvbnm'
            },
            'Permission': 'FULL_CONTROL'
        }, {
            'Grantee': {
                'URI': 'http://acs.amazonaws.com/groups/global/AllUsers'
            },
            'Permission': 'READ'
        }],
        'Owner': {
            'DisplayName': 'testowner',
            'ID': 'sdfghjklqwertyuiopzxcvbnm'
        }
    },
    'get_bucket_cors': {
        'CORSRules': [{
            'AllowedMethods': ["GET"],
            'AllowedOrigins': ["*"],
        }]
    },
    'get_bucket_lifecycle_configuration': {
        'Rules': [{
            'Expiration': {
                'Days': 1
            },
            'Prefix': 'prefix',
            'Status': 'Enabled',
            'ID': 'asdfghjklpoiuytrewq'
        }]
    },
    'get_bucket_location': {
        'LocationConstraint': 'EU'
    },
    'get_bucket_logging': {
        'LoggingEnabled': {
            'TargetBucket': 'my-bucket',
            'TargetPrefix': 'prefix'
        }
    },
    'get_bucket_notification_configuration': {
        'LambdaFunctionConfigurations': [{
            'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:111111222222:function:my-function',
            'Id': 'zxcvbnmlkjhgfdsa',
            'Events': ["s3:ObjectCreated:*"],
            'Filter': {
                'Key': {
                    'FilterRules': [{
                        'Name': 'prefix',
                        'Value': 'string'
                    }]
                }
            }
        }]
    },
    'get_bucket_policy': {
        'Policy':
            '{"Version":"2012-10-17","Statement":[{"Sid":"","Effect":"Allow","Principal":{"AWS":"arn:aws:iam::111111222222:root"},"Action":"s3:PutObject","Resource":"arn:aws:s3:::my-bucket/*"}]}'
    },
    'get_bucket_replication': {
        'ReplicationConfiguration': {
            'Role': 'arn:aws:iam::11111222222:my-role',
            'Rules': [{
                'ID': "r1",
                'Prefix': "prefix",
                'Status': "Enabled",
                'Destination': {
                    'Bucket': "arn:aws:s3:::my-bucket"
                }
            }]
        }
    },
    'get_bucket_request_payment': {'Payer': 'Requester'},
    'get_bucket_tagging': {
        'TagSet': [{
            'Key': 'c',
            'Value': 'd'
        }, {
            'Key': 'a',
            'Value': 'b',
        }]
    },
    'get_bucket_versioning': {
        'Status': 'Enabled'
    },
    'get_bucket_website': {
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    }
}


def setup_module(boto_conn):
    pytest.helpers.setup_loader({boto_s3_bucket: {'__utils__': pytest.utils}})
    boto_s3_bucket.__init__(pytest.opts)


def test_that_when_checking_if_a_bucket_exists_and_a_bucket_exists_the_bucket_exists_method_returns_true(boto_conn):
    '''
    Tests checking s3 bucket existence when the s3 bucket already exists
    '''
    boto_conn.head_bucket.return_value = None
    result = boto_s3_bucket.exists(Bucket='mybucket', **pytest.conn_parameters)

    assert result['exists'] is True

def test_that_when_checking_if_a_bucket_exists_and_a_bucket_does_not_exist_the_bucket_exists_method_returns_false(boto_conn):
    '''
    Tests checking s3 bucket existence when the s3 bucket does not exist
    '''
    boto_conn.head_bucket.side_effect = e404_error
    result = boto_s3_bucket.exists(Bucket='mybucket', **pytest.conn_parameters)

    assert result['exists'] is False

def test_that_when_checking_if_a_bucket_exists_and_boto3_returns_an_error_the_bucket_exists_method_returns_error(boto_conn):
    '''
    Tests checking s3 bucket existence when boto returns an error
    '''
    boto_conn.head_bucket.side_effect = exceptions.ClientError(error_content, 'head_bucket')
    result = boto_s3_bucket.exists(Bucket='mybucket', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('head_bucket')

def test_that_when_creating_a_bucket_succeeds_the_create_bucket_method_returns_true(boto_conn):
    '''
    tests True bucket created.
    '''
    boto_conn.create_bucket.return_value = create_ret
    result = boto_s3_bucket.create(Bucket='mybucket',
                                   LocationConstraint='nowhere',
                                    **pytest.conn_parameters)

    assert result['created'] is True

def test_that_when_creating_a_bucket_fails_the_create_bucket_method_returns_error(boto_conn):
    '''
    tests False bucket not created.
    '''
    boto_conn.create_bucket.side_effect = exceptions.ClientError(error_content, 'create_bucket')
    result = boto_s3_bucket.create(Bucket='mybucket',
                                   LocationConstraint='nowhere',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('create_bucket')

def test_that_when_deleting_a_bucket_succeeds_the_delete_bucket_method_returns_true(boto_conn):
    '''
    tests True bucket deleted.
    '''
    result = boto_s3_bucket.delete(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_a_bucket_fails_the_delete_bucket_method_returns_false(boto_conn):
    '''
    tests False bucket not deleted.
    '''
    boto_conn.delete_bucket.side_effect = exceptions.ClientError(error_content, 'delete_bucket')
    result = boto_s3_bucket.delete(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result['deleted'] is False

def test_that_when_describing_bucket_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if bucket exists
    '''
    for key, value in six.iteritems(config_ret):
        getattr(boto_conn.conn, key).return_value = deepcopy(value)

    result = boto_s3_bucket.describe(Bucket='mybucket', **pytest.conn_parameters)

    assert result['bucket']

def test_that_when_describing_bucket_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters if bucket does not exist
    '''
    boto_conn.get_bucket_acl.side_effect = not_found_error
    result = boto_s3_bucket.describe(Bucket='mybucket', **pytest.conn_parameters)

    assert result['bucket'] is None

def test_that_when_describing_bucket_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.get_bucket_acl.side_effect = exceptions.ClientError(error_content, 'get_bucket_acl')
    result = boto_s3_bucket.describe(Bucket='mybucket', **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_listing_buckets_succeeds_the_list_buckets_method_returns_true(boto_conn):
    '''
    tests True buckets listed.
    '''
    boto_conn.list_buckets.return_value = deepcopy(list_ret)
    result = boto_s3_bucket.list(**pytest.conn_parameters)

    assert result['Buckets']

def test_that_when_listing_bucket_fails_the_list_bucket_method_returns_false(boto_conn):
    '''
    tests False no bucket listed.
    '''
    ret = deepcopy(list_ret)
    log.info(ret)
    ret['Buckets'] = list()
    boto_conn.list_buckets.return_value = ret
    result = boto_s3_bucket.list(**pytest.conn_parameters)
    assert not result['Buckets']

def test_that_when_listing_bucket_fails_the_list_bucket_method_returns_error(boto_conn):
    '''
    tests False bucket error.
    '''
    boto_conn.list_buckets.side_effect = exceptions.ClientError(error_content, 'list_buckets')
    result = boto_s3_bucket.list(**pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('list_buckets')

def test_that_when_putting_acl_succeeds_the_put_acl_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_acl(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_acl_fails_the_put_acl_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_acl.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_acl')
    result = boto_s3_bucket.put_acl(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_acl')

def test_that_when_putting_cors_succeeds_the_put_cors_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_cors(Bucket='mybucket', CORSRules='[]',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_cors_fails_the_put_cors_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_cors.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_cors')
    result = boto_s3_bucket.put_cors(Bucket='mybucket', CORSRules='[]',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_cors')

def test_that_when_putting_lifecycle_configuration_succeeds_the_put_lifecycle_configuration_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_lifecycle_configuration(Bucket='mybucket',
                                    Rules='[]',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_lifecycle_configuration_fails_the_put_lifecycle_configuration_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_lifecycle_configuration.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_lifecycle_configuration')
    result = boto_s3_bucket.put_lifecycle_configuration(Bucket='mybucket',
                                    Rules='[]',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_lifecycle_configuration')

def test_that_when_putting_logging_succeeds_the_put_logging_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_logging(Bucket='mybucket',
                                    TargetBucket='arn:::::',
                                    TargetPrefix='asdf',
                                    TargetGrants='[]',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_logging_fails_the_put_logging_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_logging.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_logging')
    result = boto_s3_bucket.put_logging(Bucket='mybucket',
                                    TargetBucket='arn:::::',
                                    TargetPrefix='asdf',
                                    TargetGrants='[]',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_logging')

def test_that_when_putting_notification_configuration_succeeds_the_put_notification_configuration_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_notification_configuration(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_notification_configuration_fails_the_put_notification_configuration_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_notification_configuration.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_notification_configuration')
    result = boto_s3_bucket.put_notification_configuration(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_notification_configuration')

def test_that_when_putting_policy_succeeds_the_put_policy_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_policy(Bucket='mybucket',
                                    Policy='{}',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_policy_fails_the_put_policy_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_policy.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_policy')
    result = boto_s3_bucket.put_policy(Bucket='mybucket',
                                    Policy='{}',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_policy')

def test_that_when_putting_replication_succeeds_the_put_replication_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_replication(Bucket='mybucket',
                                    Role='arn:aws:iam:::',
                                    Rules='[]',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_replication_fails_the_put_replication_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_replication.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_replication')
    result = boto_s3_bucket.put_replication(Bucket='mybucket',
                                    Role='arn:aws:iam:::',
                                    Rules='[]',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_replication')

def test_that_when_putting_request_payment_succeeds_the_put_request_payment_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_request_payment(Bucket='mybucket',
                                    Payer='Requester',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_request_payment_fails_the_put_request_payment_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_request_payment.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_request_payment')
    result = boto_s3_bucket.put_request_payment(Bucket='mybucket',
                                    Payer='Requester',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_request_payment')

def test_that_when_putting_tagging_succeeds_the_put_tagging_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_tagging(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_tagging_fails_the_put_tagging_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_tagging.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_tagging')
    result = boto_s3_bucket.put_tagging(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_tagging')

def test_that_when_putting_versioning_succeeds_the_put_versioning_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_versioning(Bucket='mybucket',
                                    Status='Enabled',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_versioning_fails_the_put_versioning_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_versioning.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_versioning')
    result = boto_s3_bucket.put_versioning(Bucket='mybucket',
                                    Status='Enabled',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_versioning')

def test_that_when_putting_website_succeeds_the_put_website_method_returns_true(boto_conn):
    '''
    tests True bucket updated.
    '''
    result = boto_s3_bucket.put_website(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_putting_website_fails_the_put_website_method_returns_error(boto_conn):
    '''
    tests False bucket not updated.
    '''
    boto_conn.put_bucket_website.side_effect = exceptions.ClientError(error_content,
                   'put_bucket_website')
    result = boto_s3_bucket.put_website(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_bucket_website')

def test_that_when_deleting_cors_succeeds_the_delete_cors_method_returns_true(boto_conn):
    '''
    tests True bucket attribute deleted.
    '''
    result = boto_s3_bucket.delete_cors(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_cors_fails_the_delete_cors_method_returns_error(boto_conn):
    '''
    tests False bucket attribute not deleted.
    '''
    boto_conn.delete_bucket_cors.side_effect = exceptions.ClientError(error_content,
                   'delete_bucket_cors')
    result = boto_s3_bucket.delete_cors(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('delete_bucket_cors')

def test_that_when_deleting_lifecycle_configuration_succeeds_the_delete_lifecycle_configuration_method_returns_true(boto_conn):
    '''
    tests True bucket attribute deleted.
    '''
    result = boto_s3_bucket.delete_lifecycle_configuration(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_lifecycle_configuration_fails_the_delete_lifecycle_configuration_method_returns_error(boto_conn):
    '''
    tests False bucket attribute not deleted.
    '''
    boto_conn.delete_bucket_lifecycle.side_effect = exceptions.ClientError(error_content,
                   'delete_bucket_lifecycle_configuration')
    result = boto_s3_bucket.delete_lifecycle_configuration(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('delete_bucket_lifecycle_configuration')

def test_that_when_deleting_policy_succeeds_the_delete_policy_method_returns_true(boto_conn):
    '''
    tests True bucket attribute deleted.
    '''
    result = boto_s3_bucket.delete_policy(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_policy_fails_the_delete_policy_method_returns_error(boto_conn):
    '''
    tests False bucket attribute not deleted.
    '''
    boto_conn.delete_bucket_policy.side_effect = exceptions.ClientError(error_content,
                   'delete_bucket_policy')
    result = boto_s3_bucket.delete_policy(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('delete_bucket_policy')

def test_that_when_deleting_replication_succeeds_the_delete_replication_method_returns_true(boto_conn):
    '''
    tests True bucket attribute deleted.
    '''
    result = boto_s3_bucket.delete_replication(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_replication_fails_the_delete_replication_method_returns_error(boto_conn):
    '''
    tests False bucket attribute not deleted.
    '''
    boto_conn.delete_bucket_replication.side_effect = exceptions.ClientError(error_content,
                   'delete_bucket_replication')
    result = boto_s3_bucket.delete_replication(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('delete_bucket_replication')

def test_that_when_deleting_tagging_succeeds_the_delete_tagging_method_returns_true(boto_conn):
    '''
    tests True bucket attribute deleted.
    '''
    result = boto_s3_bucket.delete_tagging(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_tagging_fails_the_delete_tagging_method_returns_error(boto_conn):
    '''
    tests False bucket attribute not deleted.
    '''
    boto_conn.delete_bucket_tagging.side_effect = exceptions.ClientError(error_content,
                   'delete_bucket_tagging')
    result = boto_s3_bucket.delete_tagging(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('delete_bucket_tagging')

def test_that_when_deleting_website_succeeds_the_delete_website_method_returns_true(boto_conn):
    '''
    tests True bucket attribute deleted.
    '''
    result = boto_s3_bucket.delete_website(Bucket='mybucket',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_website_fails_the_delete_website_method_returns_error(boto_conn):
    '''
    tests False bucket attribute not deleted.
    '''
    boto_conn.delete_bucket_website.side_effect = exceptions.ClientError(error_content,
                   'delete_bucket_website')
    result = boto_s3_bucket.delete_website(Bucket='mybucket',
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('delete_bucket_website')
