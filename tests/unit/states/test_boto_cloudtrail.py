# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging
import logging

# Import Salt libs
import salt.loader

# Import Fractus Libs
import fractus.cloudstates.boto_cloudtrail as boto_cloudtrail

# Import Testing Libs
import pytest
from mock import MagicMock, patch
pytestmark = pytest.mark.skip('all tests still WIP')

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
    serializers = salt.loader.serializers(pytest.opts)
    return {
        boto_cloudtrail: {
            '__opts__': pytest.opts,
            '__salt__': pytest.modules,
            '__utils__': pytest.utils,
            '__states__': pytest.states,
            '__serializers__': serializers,
        }
    }


def test_present_when_trail_does_not_exist(boto_conn):
    '''
    Tests present on a trail that does not exist.
    '''
    boto_conn.get_trail_status.side_effect = [not_found_error, status_ret]
    boto_conn.create_trail.return_value = trail_ret
    boto_conn.describe_trails.return_value = {'trailList': [trail_ret]}
    with patch.dict(boto_conn.funcs, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = pytest.states['boto_cloudtrail.present'](
                     'trail present',
                     Name=trail_ret['Name'],
                     S3BucketName=trail_ret['S3BucketName'])

    assert result['result']
    assert result['changes']['new']['trail']['Name'] == \
                     trail_ret['Name']

def test_present_when_trail_exists(boto_conn):
    boto_conn.get_trail_status.return_value = status_ret
    boto_conn.create_trail.return_value = trail_ret
    boto_conn.describe_trails.return_value = {'trailList': [trail_ret]}
    with patch.dict(boto_conn.funcs, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = pytest.states['boto_cloudtrail.present'](
                     'trail present',
                     Name=trail_ret['Name'],
                     S3BucketName=trail_ret['S3BucketName'],
                     LoggingEnabled=False)
    assert result['result']
    assert result['changes'] == {}

def test_present_with_failure(boto_conn):
    boto_conn.get_trail_status.side_effect = [not_found_error, status_ret]
    boto_conn.create_trail.side_effect = exceptions.ClientError(error_content, 'create_trail')
    with patch.dict(boto_conn.funcs, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = pytest.states['boto_cloudtrail.present'](
                     'trail present',
                     Name=trail_ret['Name'],
                     S3BucketName=trail_ret['S3BucketName'],
                     LoggingEnabled=False)
    assert not result['result']
    assert 'An error occurred' in result['comment']

def test_absent_when_trail_does_not_exist(boto_conn):
    '''
    Tests absent on a trail that does not exist.
    '''
    boto_conn.get_trail_status.side_effect = not_found_error
    result = pytest.states['boto_cloudtrail.absent']('test', 'mytrail')
    assert result['result']
    assert result['changes'] == {}

def test_absent_when_trail_exists(boto_conn):
    boto_conn.get_trail_status.return_value = status_ret
    result = pytest.states['boto_cloudtrail.absent']('test', trail_ret['Name'])
    assert result['result']
    assert result['changes']['new']['trail'] == None

def test_absent_with_failure(boto_conn):
    boto_conn.get_trail_status.return_value = status_ret
    boto_conn.delete_trail.side_effect = exceptions.ClientError(error_content, 'delete_trail')
    result = pytest.states['boto_cloudtrail.absent']('test', trail_ret['Name'])
    assert not result['result']
    assert 'An error occurred' in result['comment']
