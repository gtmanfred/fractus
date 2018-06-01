# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging

# Import Fractus libs
import fractus.cloudmodules.boto_cloudtrail as boto_cloudtrail

# Import Testing libs
import pytest
from mock import MagicMock, patch


boto3 = pytest.importorskip('boto3', minversion='1.2.1')
boto = pytest.importorskip('boto')
exceptions = pytest.importorskip('botocore.exceptions')

log = logging.getLogger(__name__)

error_message = 'An error occurred (101) when calling the {0} operation: Test-defined error'
not_found_error = exceptions.ClientError({
    'Error': {
        'Code': 'TrailNotFoundException',
        'Message': "Test-defined error"
    }
}, 'msg')
error_content = {
  'Error': {
    'Code': 101,
    'Message': "Test-defined error"
  }
}
trail_ret = dict(Name='testtrail',
                 IncludeGlobalServiceEvents=True,
                 KmsKeyId=None,
                 LogFileValidationEnabled=False,
                 S3BucketName='auditinfo',
                 TrailARN='arn:aws:cloudtrail:us-east-1:214351231622:trail/testtrail')
status_ret = dict(IsLogging=False,
                  LatestCloudWatchLogsDeliveryError=None,
                  LatestCloudWatchLogsDeliveryTime=None,
                  LatestDeliveryError=None,
                  LatestDeliveryTime=None,
                  LatestDigestDeliveryError=None,
                  LatestDigestDeliveryTime=None,
                  LatestNotificationError=None,
                  LatestNotificationTime=None,
                  StartLoggingTime=None,
                  StopLoggingTime=None)


def setup_module():
    pytest.helpers.setup_loader({
        boto_cloudtrail: {
            '__utils__': pytest.utils,
        }
    })
    boto_cloudtrail.__init__(pytest.opts)


def test_that_when_checking_if_a_trail_exists_and_a_trail_exists_the_trail_exists_method_returns_true(boto_conn):
    '''
    Tests checking cloudtrail trail existence when the cloudtrail trail already exists
    '''
    boto_conn.get_trail_status.return_value = trail_ret
    result = boto_cloudtrail.exists(Name=trail_ret['Name'], **pytest.conn_parameters)

    assert result['exists'] is True

def test_that_when_checking_if_a_trail_exists_and_a_trail_does_not_exist_the_trail_exists_method_returns_false(boto_conn):
    '''
    Tests checking cloudtrail trail existence when the cloudtrail trail does not exist
    '''
    boto_conn.get_trail_status.side_effect = not_found_error
    result = boto_cloudtrail.exists(Name='mytrail', **pytest.conn_parameters)

    assert result['exists'] is False

def test_that_when_checking_if_a_trail_exists_and_boto3_returns_an_error_the_trail_exists_method_returns_error(boto_conn):
    '''
    Tests checking cloudtrail trail existence when boto returns an error
    '''
    boto_conn.get_trail_status.side_effect = exceptions.ClientError(error_content, 'get_trail_status')
    result = boto_cloudtrail.exists(Name='mytrail', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('get_trail_status')

def test_that_when_creating_a_trail_succeeds_the_create_trail_method_returns_true(boto_conn):
    '''
    tests True trail created.
    '''
    boto_conn.create_trail.return_value = trail_ret
    result = boto_cloudtrail.create(Name=trail_ret['Name'],
                                    S3BucketName=trail_ret['S3BucketName'],
                                    **pytest.conn_parameters)

    assert result['created'] is True

def test_that_when_creating_a_trail_fails_the_create_trail_method_returns_error(boto_conn):
    '''
    tests False trail not created.
    '''
    boto_conn.create_trail.side_effect = exceptions.ClientError(error_content, 'create_trail')
    result = boto_cloudtrail.create(Name=trail_ret['Name'],
                                    S3BucketName=trail_ret['S3BucketName'],
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('create_trail')

def test_that_when_deleting_a_trail_succeeds_the_delete_trail_method_returns_true(boto_conn):
    '''
    tests True trail deleted.
    '''
    result = boto_cloudtrail.delete(Name='testtrail',
                                    **pytest.conn_parameters)

    assert result['deleted'] is True

def test_that_when_deleting_a_trail_fails_the_delete_trail_method_returns_false(boto_conn):
    '''
    tests False trail not deleted.
    '''
    boto_conn.delete_trail.side_effect = exceptions.ClientError(error_content, 'delete_trail')
    result = boto_cloudtrail.delete(Name='testtrail',
                                    **pytest.conn_parameters)
    assert result['deleted'] is False

def test_that_when_describing_trail_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if trail exists
    '''
    boto_conn.describe_trails.return_value = {'trailList': [trail_ret]}

    result = boto_cloudtrail.describe(Name=trail_ret['Name'], **pytest.conn_parameters)

    assert result['trail']

def test_that_when_describing_trail_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters if trail does not exist
    '''
    boto_conn.describe_trails.side_effect = not_found_error
    result = boto_cloudtrail.describe(Name='testtrail', **pytest.conn_parameters)

    assert result['trail'] is None

def test_that_when_describing_trail_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.describe_trails.side_effect = exceptions.ClientError(error_content, 'get_trail')
    result = boto_cloudtrail.describe(Name='testtrail', **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_getting_status_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests getting status if trail exists
    '''
    boto_conn.get_trail_status.return_value = status_ret

    result = boto_cloudtrail.status(Name=trail_ret['Name'], **pytest.conn_parameters)

    assert result['trail']

def test_that_when_getting_status_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests getting status if trail does not exist
    '''
    boto_conn.get_trail_status.side_effect = not_found_error
    result = boto_cloudtrail.status(Name='testtrail', **pytest.conn_parameters)

    assert result['trail'] is None

def test_that_when_getting_status_on_client_error_it_returns_error(boto_conn):
    '''
    Tests getting status failure
    '''
    boto_conn.get_trail_status.side_effect = exceptions.ClientError(error_content, 'get_trail_status')
    result = boto_cloudtrail.status(Name='testtrail', **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_listing_trails_succeeds_the_list_trails_method_returns_true(boto_conn):
    '''
    tests True trails listed.
    '''
    boto_conn.describe_trails.return_value = {'trailList': [trail_ret]}
    result = boto_cloudtrail.list(**pytest.conn_parameters)

    assert result['trails']

def test_that_when_listing_trail_fails_the_list_trail_method_returns_false(boto_conn):
    '''
    tests False no trail listed.
    '''
    boto_conn.describe_trails.return_value = {'trailList': []}
    result = boto_cloudtrail.list(**pytest.conn_parameters)
    assert not result['trails']

def test_that_when_listing_trail_fails_the_list_trail_method_returns_error(boto_conn):
    '''
    tests False trail error.
    '''
    boto_conn.describe_trails.side_effect = exceptions.ClientError(error_content, 'list_trails')
    result = boto_cloudtrail.list(**pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('list_trails')

def test_that_when_updating_a_trail_succeeds_the_update_trail_method_returns_true(boto_conn):
    '''
    tests True trail updated.
    '''
    boto_conn.update_trail.return_value = trail_ret
    result = boto_cloudtrail.update(Name=trail_ret['Name'],
                                    S3BucketName=trail_ret['S3BucketName'],
                                    **pytest.conn_parameters)

    assert result['updated'] is True

def test_that_when_updating_a_trail_fails_the_update_trail_method_returns_error(boto_conn):
    '''
    tests False trail not updated.
    '''
    boto_conn.update_trail.side_effect = exceptions.ClientError(error_content, 'update_trail')
    result = boto_cloudtrail.update(Name=trail_ret['Name'],
                                    S3BucketName=trail_ret['S3BucketName'],
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('update_trail')

def test_that_when_starting_logging_succeeds_the_start_logging_method_returns_true(boto_conn):
    '''
    tests True logging started.
    '''
    result = boto_cloudtrail.start_logging(Name=trail_ret['Name'], **pytest.conn_parameters)

    assert result['started'] is True

def test_that_when_start_logging_fails_the_start_logging_method_returns_false(boto_conn):
    '''
    tests False logging not started.
    '''
    boto_conn.describe_trails.return_value = {'trailList': []}
    boto_conn.start_logging.side_effect = exceptions.ClientError(error_content, 'start_logging')
    result = boto_cloudtrail.start_logging(Name=trail_ret['Name'], **pytest.conn_parameters)
    assert result['started'] is False

def test_that_when_stopping_logging_succeeds_the_stop_logging_method_returns_true(boto_conn):
    '''
    tests True logging stopped.
    '''
    result = boto_cloudtrail.stop_logging(Name=trail_ret['Name'], **pytest.conn_parameters)

    assert result['stopped'] is True

def test_that_when_stop_logging_fails_the_stop_logging_method_returns_false(boto_conn):
    '''
    tests False logging not stopped.
    '''
    boto_conn.describe_trails.return_value = {'trailList': []}
    boto_conn.stop_logging.side_effect = exceptions.ClientError(error_content, 'stop_logging')
    result = boto_cloudtrail.stop_logging(Name=trail_ret['Name'], **pytest.conn_parameters)
    assert result['stopped'] is False

def test_that_when_adding_tags_succeeds_the_add_tags_method_returns_true(boto_conn):
    '''
    tests True tags added.
    '''
    with patch.dict(boto_cloudtrail.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_cloudtrail.add_tags(Name=trail_ret['Name'], a='b', **pytest.conn_parameters)

    assert result['tagged'] is True

def test_that_when_adding_tags_fails_the_add_tags_method_returns_false(boto_conn):
    '''
    tests False tags not added.
    '''
    boto_conn.add_tags.side_effect = exceptions.ClientError(error_content, 'add_tags')
    with patch.dict(boto_cloudtrail.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_cloudtrail.add_tags(Name=trail_ret['Name'], a='b', **pytest.conn_parameters)
    assert result['tagged'] is False

def test_that_when_removing_tags_succeeds_the_remove_tags_method_returns_true(boto_conn):
    '''
    tests True tags removed.
    '''
    with patch.dict(boto_cloudtrail.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_cloudtrail.remove_tags(Name=trail_ret['Name'], a='b', **pytest.conn_parameters)

    assert result['tagged'] is True

def test_that_when_removing_tags_fails_the_remove_tags_method_returns_false(boto_conn):
    '''
    tests False tags not removed.
    '''
    boto_conn.remove_tags.side_effect = exceptions.ClientError(error_content, 'remove_tags')
    with patch.dict(boto_cloudtrail.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_cloudtrail.remove_tags(Name=trail_ret['Name'], a='b', **pytest.conn_parameters)
    assert result['tagged'] is False

def test_that_when_listing_tags_succeeds_the_list_tags_method_returns_true(boto_conn):
    '''
    tests True tags listed.
    '''
    with patch.dict(boto_cloudtrail.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_cloudtrail.list_tags(Name=trail_ret['Name'], **pytest.conn_parameters)

    assert result['tags'] == {}

def test_that_when_listing_tags_fails_the_list_tags_method_returns_false(boto_conn):
    '''
    tests False tags not listed.
    '''
    boto_conn.list_tags.side_effect = exceptions.ClientError(error_content, 'list_tags')
    with patch.dict(boto_cloudtrail.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_cloudtrail.list_tags(Name=trail_ret['Name'], **pytest.conn_parameters)
    assert result['error']
