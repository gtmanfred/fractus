# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging

# Import Fractus libs
import fractus.cloudmodules.boto_cloudwatch_event as boto_cloudwatch_event

# Import Testing libs
import pytest
from mock import MagicMock, patch

log = logging.getLogger(__name__)

boto = pytest.importorskip('boto')
boto3 = pytest.importorskip('boto3')
exceptions = pytest.importorskip('botocore.exceptions')


error_message = 'An error occurred (101) when calling the {0} operation: Test-defined error'
not_found_error = exceptions.ClientError({
    'Error': {
        'Code': 'ResourceNotFoundException',
        'Message': "Test-defined error"
    }
}, 'msg')
error_content = {
  'Error': {
    'Code': 101,
    'Message': "Test-defined error"
  }
}
rule_name = 'test_thing_type'
rule_desc = 'test_thing_type_desc'
rule_sched = 'rate(20 min)'
rule_arn = 'arn:::::rule/arn'
rule_ret = dict(
    Arn=rule_arn,
    Description=rule_desc,
    EventPattern=None,
    Name=rule_name,
    RoleArn=None,
    ScheduleExpression=rule_sched,
    State='ENABLED'
)
create_rule_ret = dict(
    Name=rule_name,
)
target_ret = dict(
    Id='target1',
)


def setup_function(function):
    pytest.helpers.setup_loader({
        boto_cloudwatch_event: {
            '__utils__': pytest.utils,
        },
    })
    boto_cloudwatch_event.__virtual__()
    boto_cloudwatch_event.__init__(pytest.opts)


def test_that_when_checking_if_a_rule_exists_and_a_rule_exists_the_rule_exists_method_returns_true(boto_conn):
    '''
    Tests checking event existence when the event already exists
    '''
    boto_conn.list_rules.return_value = {'Rules': [rule_ret]}
    result = boto_cloudwatch_event.exists(Name=rule_name, **pytest.conn_parameters)

    assert result['exists'] is True

def test_that_when_checking_if_a_rule_exists_and_a_rule_does_not_exist_the_exists_method_returns_false(boto_conn):
    '''
    Tests checking rule existence when the rule does not exist
    '''
    boto_conn.list_rules.return_value = {'Rules': []}
    result = boto_cloudwatch_event.exists(Name=rule_name, **pytest.conn_parameters)

    assert result['exists'] is False

def test_that_when_checking_if_a_rule_exists_and_boto3_returns_an_error_the_rule_exists_method_returns_error(boto_conn):
    '''
    Tests checking rule existence when boto returns an error
    '''
    boto_conn.list_rules.side_effect = exceptions.ClientError(error_content, 'list_rules')
    result = boto_cloudwatch_event.exists(Name=rule_name, **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('list_rules')

def test_that_when_describing_rule_and_rule_exists_the_describe_rule_method_returns_rule(boto_conn):
    '''
    Tests describe rule for an existing rule
    '''
    boto_conn.describe_rule.return_value = rule_ret
    result = boto_cloudwatch_event.describe(Name=rule_name, **pytest.conn_parameters)

    assert result.get('rule') == rule_ret

def test_that_when_describing_rule_and_rule_does_not_exists_the_describe_method_returns_none(boto_conn):
    '''
    Tests describe rule for an non existent rule
    '''
    boto_conn.describe_rule.side_effect = not_found_error
    result = boto_cloudwatch_event.describe(Name=rule_name, **pytest.conn_parameters)

    assert result.get('error') is not None

def test_that_when_describing_rule_and_boto3_returns_error_the_describe_method_returns_error(boto_conn):
    boto_conn.describe_rule.side_effect = exceptions.ClientError(error_content, 'describe_rule')
    result = boto_cloudwatch_event.describe(Name=rule_name, **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('describe_rule')

def test_that_when_creating_a_rule_succeeds_the_create_rule_method_returns_true(boto_conn):
    '''
    tests True when rule created
    '''
    boto_conn.put_rule.return_value = create_rule_ret
    result = boto_cloudwatch_event.create_or_update(Name=rule_name,
                                        Description=rule_desc,
                                        ScheduleExpression=rule_sched,
                                        **pytest.conn_parameters)
    assert result['created'] is True

def test_that_when_creating_a_rule_fails_the_create_method_returns_error(boto_conn):
    '''
    tests False when rule not created
    '''
    boto_conn.put_rule.side_effect = exceptions.ClientError(error_content, 'put_rule')
    result = boto_cloudwatch_event.create_or_update(Name=rule_name,
                                        Description=rule_desc,
                                        ScheduleExpression=rule_sched,
                                        **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_rule')

def test_that_when_deleting_a_rule_succeeds_the_delete_method_returns_true(boto_conn):
    '''
    tests True when delete rule succeeds
    '''
    boto_conn.delete_rule.return_value = {}
    result = boto_cloudwatch_event.delete(Name=rule_name, **pytest.conn_parameters)

    assert result.get('deleted') is True
    assert result.get('error') is None

def test_that_when_deleting_a_rule_fails_the_delete_method_returns_error(boto_conn):
    '''
    tests False when delete rule fails
    '''
    boto_conn.delete_rule.side_effect = exceptions.ClientError(error_content, 'delete_rule')
    result = boto_cloudwatch_event.delete(Name=rule_name, **pytest.conn_parameters)
    assert result.get('deleted') is False
    assert result.get('error', {}).get('message') == error_message.format('delete_rule')

def test_that_when_listing_targets_and_rule_exists_the_list_targets_method_returns_targets(boto_conn):
    '''
    Tests listing targets for an existing rule
    '''
    boto_conn.list_targets_by_rule.return_value = {'Targets': [target_ret]}
    result = boto_cloudwatch_event.list_targets(Rule=rule_name, **pytest.conn_parameters)

    assert result.get('targets') == [target_ret]

def test_that_when_listing_targets_and_rule_does_not_exist_the_list_targets_method_returns_error(boto_conn):
    '''
    Tests list targets for an non existent rule
    '''
    boto_conn.list_targets_by_rule.side_effect = not_found_error
    result = boto_cloudwatch_event.list_targets(Rule=rule_name, **pytest.conn_parameters)

    assert result.get('error') is not None

def test_that_when_putting_targets_succeeds_the_put_target_method_returns_no_failures(boto_conn):
    '''
    tests None when targets added
    '''
    boto_conn.put_targets.return_value = {'FailedEntryCount': 0}
    result = boto_cloudwatch_event.put_targets(Rule=rule_name,
                                        Targets=[],
                                        **pytest.conn_parameters)
    assert result['failures'] is None

def test_that_when_putting_targets_fails_the_put_targets_method_returns_error(boto_conn):
    '''
    tests False when thing type not created
    '''
    boto_conn.put_targets.side_effect = exceptions.ClientError(error_content, 'put_targets')
    result = boto_cloudwatch_event.put_targets(Rule=rule_name,
                                        Targets=[],
                                        **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('put_targets')

def test_that_when_removing_targets_succeeds_the_remove_targets_method_returns_true(boto_conn):
    '''
    tests True when remove targets succeeds
    '''
    boto_conn.remove_targets.return_value = {'FailedEntryCount': 0}
    result = boto_cloudwatch_event.remove_targets(Rule=rule_name, Ids=[], **pytest.conn_parameters)

    assert result['failures'] is None
    assert result.get('error') is None

def test_that_when_removing_targets_fails_the_remove_targets_method_returns_error(boto_conn):
    '''
    tests False when remove targets fails
    '''
    boto_conn.remove_targets.side_effect = exceptions.ClientError(error_content, 'remove_targets')
    result = boto_cloudwatch_event.remove_targets(Rule=rule_name, Ids=[], **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('remove_targets')
