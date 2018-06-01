# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging

# Import Fractus libs
import salt.modules.boto_iot as boto_iot

# Import Testing Libs
import pytest


boto3 = pytest.importorskip('boto3', minversion='1.2.1')
boto = pytest.importorskip('boto')
botocore = pytest.importorskip('botocore', minversion='1.3.41')
exceptions = pytest.importorskip('botocore.exceptions')


log = logging.getLogger(__name__)


error_message = 'An error occurred (101) when calling the {0} operation: Test-defined error'
not_found_error = exceptions.ClientError({
    'Error': {
        'Code': 'ResourceNotFoundException',
        'Message': "Test-defined error"
    }
}, 'msg')
topic_rule_not_found_error = exceptions.ClientError({
    'Error': {
        'Code': 'UnauthorizedException',
        'Message': "Test-defined error"
    }
}, 'msg')
error_content = {
  'Error': {
    'Code': 101,
    'Message': "Test-defined error"
  }
}
policy_ret = dict(policyName='testpolicy',
                  policyDocument='{"Version": "2012-10-17", "Statement": [{"Action": ["iot:Publish"], "Resource": ["*"], "Effect": "Allow"}]}',
                  policyArn='arn:aws:iot:us-east-1:123456:policy/my_policy',
                  policyVersionId=1,
                  defaultVersionId=1)
topic_rule_ret = dict(ruleName='testrule',
                  sql="SELECT * FROM 'iot/test'",
                  description='topic rule description',
                  createdAt='1970-01-01',
                  actions=[{'lambda': {'functionArn': 'arn:aws:::function'}}],
                  ruleDisabled=True)

thing_type_name = 'test_thing_type'
thing_type_desc = 'test_thing_type_desc'
thing_type_attr_1 = 'test_thing_type_search_attr_1'
thing_type_ret = dict(
    thingTypeName=thing_type_name,
    thingTypeProperties=dict(
        thingTypeDescription=thing_type_desc,
        searchableAttributes=[thing_type_attr_1],
    ),
    thingTypeMetadata=dict(
        deprecated=False,
        creationDate='test_thing_type_create_date'
    )
)
thing_type_arn = 'test_thing_type_arn'
create_thing_type_ret = dict(
    thingTypeName=thing_type_name,
    thingTypeArn=thing_type_arn
)


def setup_module():
    pytest.helpers.setup_loader({boto_iot: {'__utils__': pytest.utils}})
    boto_iot.__init__(pytest.opts)


def test_that_when_checking_if_a_thing_type_exists_and_a_thing_type_exists_the_thing_type_exists_method_returns_true(boto_conn):
    '''
    Tests checking iot thing type existence when the iot thing type already exists
    '''
    boto_conn.describe_thing_type.return_value = thing_type_ret
    result = boto_iot.thing_type_exists(thingTypeName=thing_type_name, **pytest.conn_parameters)

    assert result['exists']

def test_that_when_checking_if_a_thing_type_exists_and_a_thing_type_does_not_exist_the_thing_type_exists_method_returns_false(boto_conn):
    '''
    Tests checking iot thing type existence when the iot thing type does not exist
    '''
    boto_conn.describe_thing_type.side_effect = not_found_error
    result = boto_iot.thing_type_exists(thingTypeName='non existent thing type', **pytest.conn_parameters)

    assert not result['exists']

def test_that_when_checking_if_a_thing_type_exists_and_boto3_returns_an_error_the_thing_type_exists_method_returns_error(boto_conn):
    '''
    Tests checking iot thing type existence when boto returns an error
    '''
    boto_conn.describe_thing_type.side_effect = exceptions.ClientError(error_content, 'describe_thing_type')
    result = boto_iot.thing_type_exists(thingTypeName='mythingtype', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('describe_thing_type')

def test_that_when_describing_thing_type_and_thing_type_exists_the_describe_thing_type_method_returns_thing_type(boto_conn):
    '''
    Tests describe thing type for an existing thing type
    '''
    boto_conn.describe_thing_type.return_value = thing_type_ret
    result = boto_iot.describe_thing_type(thingTypeName=thing_type_name, **pytest.conn_parameters)

    assert result.get('thing_type') == thing_type_ret

def test_that_when_describing_thing_type_and_thing_type_does_not_exists_the_describe_thing_type_method_returns_none(boto_conn):
    '''
    Tests describe thing type for an non existent thing type
    '''
    boto_conn.describe_thing_type.side_effect = not_found_error
    result = boto_iot.describe_thing_type(thingTypeName='non existent thing type', **pytest.conn_parameters)

    assert result.get('thing_type') == None

def test_that_when_describing_thing_type_and_boto3_returns_error_an_error_the_describe_thing_type_method_returns_error(boto_conn):
    boto_conn.describe_thing_type.side_effect = exceptions.ClientError(error_content, 'describe_thing_type')
    result = boto_iot.describe_thing_type(thingTypeName='mythingtype', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('describe_thing_type')

def test_that_when_creating_a_thing_type_succeeds_the_create_thing_type_method_returns_true(boto_conn):
    '''
    tests True when thing type created
    '''
    boto_conn.create_thing_type.return_value = create_thing_type_ret
    result = boto_iot.create_thing_type(thingTypeName=thing_type_name,
                                        thingTypeDescription=thing_type_desc,
                                        searchableAttributesList=[thing_type_attr_1],
                                        **pytest.conn_parameters)
    assert result['created']
    assert result['thingTypeArn'], thing_type_arn

def test_that_when_creating_a_thing_type_fails_the_create_thing_type_method_returns_error(boto_conn):
    '''
    tests False when thing type not created
    '''
    boto_conn.create_thing_type.side_effect = exceptions.ClientError(error_content, 'create_thing_type')
    result = boto_iot.create_thing_type(thingTypeName=thing_type_name,
                                        thingTypeDescription=thing_type_desc,
                                        searchableAttributesList=[thing_type_attr_1],
                                        **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('create_thing_type')

def test_that_when_deprecating_a_thing_type_succeeds_the_deprecate_thing_type_method_returns_true(boto_conn):
    '''
    tests True when deprecate thing type succeeds
    '''
    boto_conn.deprecate_thing_type.return_value = {}
    result = boto_iot.deprecate_thing_type(thingTypeName=thing_type_name,
                                           undoDeprecate=False,
                                           **pytest.conn_parameters)

    assert result.get('deprecated')
    assert result.get('error') == None

def test_that_when_deprecating_a_thing_type_fails_the_deprecate_thing_type_method_returns_error(boto_conn):
    '''
    tests False when thing type fails to deprecate
    '''
    boto_conn.deprecate_thing_type.side_effect = exceptions.ClientError(error_content, 'deprecate_thing_type')
    result = boto_iot.deprecate_thing_type(thingTypeName=thing_type_name,
                                           undoDeprecate=False,
                                           **pytest.conn_parameters)

    assert not result.get('deprecated')
    assert result.get('error', {}).get('message') == error_message.format('deprecate_thing_type')

def test_that_when_deleting_a_thing_type_succeeds_the_delete_thing_type_method_returns_true(boto_conn):
    '''
    tests True when delete thing type succeeds
    '''
    boto_conn.delete_thing_type.return_value = {}
    result = boto_iot.delete_thing_type(thingTypeName=thing_type_name, **pytest.conn_parameters)

    assert result.get('deleted')
    assert result.get('error') == None

def test_that_when_deleting_a_thing_type_fails_the_delete_thing_type_method_returns_error(boto_conn):
    '''
    tests False when delete thing type fails
    '''
    boto_conn.delete_thing_type.side_effect = exceptions.ClientError(error_content, 'delete_thing_type')
    result = boto_iot.delete_thing_type(thingTypeName=thing_type_name, **pytest.conn_parameters)
    assert not result.get('deleted')
    assert result.get('error', {}).get('message') == error_message.format('delete_thing_type')


def test_that_when_checking_if_a_policy_exists_and_a_policy_exists_the_policy_exists_method_returns_true(boto_conn):
    '''
    Tests checking iot policy existence when the iot policy already exists
    '''
    boto_conn.get_policy.return_value = {'policy': policy_ret}
    result = boto_iot.policy_exists(policyName=policy_ret['policyName'], **pytest.conn_parameters)

    assert result['exists']

def test_that_when_checking_if_a_policy_exists_and_a_policy_does_not_exist_the_policy_exists_method_returns_false(boto_conn):
    '''
    Tests checking iot policy existence when the iot policy does not exist
    '''
    boto_conn.get_policy.side_effect = not_found_error
    result = boto_iot.policy_exists(policyName='mypolicy', **pytest.conn_parameters)

    assert not result['exists']

def test_that_when_checking_if_a_policy_exists_and_boto3_returns_an_error_the_policy_exists_method_returns_error(boto_conn):
    '''
    Tests checking iot policy existence when boto returns an error
    '''
    boto_conn.get_policy.side_effect = exceptions.ClientError(error_content, 'get_policy')
    result = boto_iot.policy_exists(policyName='mypolicy', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('get_policy')

def test_that_when_creating_a_policy_succeeds_the_create_policy_method_returns_true(boto_conn):
    '''
    tests True policy created.
    '''
    boto_conn.create_policy.return_value = policy_ret
    result = boto_iot.create_policy(policyName=policy_ret['policyName'],
                                    policyDocument=policy_ret['policyDocument'],
                                    **pytest.conn_parameters)

    assert result['created']

def test_that_when_creating_a_policy_fails_the_create_policy_method_returns_error(boto_conn):
    '''
    tests False policy not created.
    '''
    boto_conn.create_policy.side_effect = exceptions.ClientError(error_content, 'create_policy')
    result = boto_iot.create_policy(policyName=policy_ret['policyName'],
                                    policyDocument=policy_ret['policyDocument'],
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('create_policy')

def test_that_when_deleting_a_policy_succeeds_the_delete_policy_method_returns_true(boto_conn):
    '''
    tests True policy deleted.
    '''
    result = boto_iot.delete_policy(policyName='testpolicy',
                                    **pytest.conn_parameters)

    assert result['deleted']

def test_that_when_deleting_a_policy_fails_the_delete_policy_method_returns_false(boto_conn):
    '''
    tests False policy not deleted.
    '''
    boto_conn.delete_policy.side_effect = exceptions.ClientError(error_content, 'delete_policy')
    result = boto_iot.delete_policy(policyName='testpolicy',
                                    **pytest.conn_parameters)
    assert not result['deleted']

def test_that_when_describing_policy_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if policy exists
    '''
    boto_conn.get_policy.return_value = {'policy': policy_ret}

    result = boto_iot.describe_policy(policyName=policy_ret['policyName'], **pytest.conn_parameters)

    assert result['policy']

def test_that_when_describing_policy_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters if policy does not exist
    '''
    boto_conn.get_policy.side_effect = not_found_error
    result = boto_iot.describe_policy(policyName='testpolicy', **pytest.conn_parameters)

    assert not result['policy']

def test_that_when_describing_policy_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.get_policy.side_effect = exceptions.ClientError(error_content, 'get_policy')
    result = boto_iot.describe_policy(policyName='testpolicy', **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_checking_if_a_policy_version_exists_and_a_policy_version_exists_the_policy_version_exists_method_returns_true(boto_conn):
    '''
    Tests checking iot policy existence when the iot policy version already exists
    '''
    boto_conn.get_policy.return_value = {'policy': policy_ret}
    result = boto_iot.policy_version_exists(policyName=policy_ret['policyName'],
                                            policyVersionId=1,
                                            **pytest.conn_parameters)

    assert result['exists']

def test_that_when_checking_if_a_policy_version_exists_and_a_policy_version_does_not_exist_the_policy_version_exists_method_returns_false(boto_conn):
    '''
    Tests checking iot policy_version existence when the iot policy_version does not exist
    '''
    boto_conn.get_policy_version.side_effect = not_found_error
    result = boto_iot.policy_version_exists(policyName=policy_ret['policyName'],
                                            policyVersionId=1,
                                            **pytest.conn_parameters)

    assert not result['exists']

def test_that_when_checking_if_a_policy_version_exists_and_boto3_returns_an_error_the_policy_version_exists_method_returns_error(boto_conn):
    '''
    Tests checking iot policy_version existence when boto returns an error
    '''
    boto_conn.get_policy_version.side_effect = exceptions.ClientError(error_content, 'get_policy_version')
    result = boto_iot.policy_version_exists(policyName=policy_ret['policyName'],
                                            policyVersionId=1,
                                            **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == error_message.format('get_policy_version')

def test_that_when_creating_a_policy_version_succeeds_the_create_policy_version_method_returns_true(boto_conn):
    '''
    tests True policy_version created.
    '''
    boto_conn.create_policy_version.return_value = policy_ret
    result = boto_iot.create_policy_version(policyName=policy_ret['policyName'],
                                    policyDocument=policy_ret['policyDocument'],
                                    **pytest.conn_parameters)

    assert result['created']

def test_that_when_creating_a_policy_version_fails_the_create_policy_version_method_returns_error(boto_conn):
    '''
    tests False policy_version not created.
    '''
    boto_conn.create_policy_version.side_effect = exceptions.ClientError(error_content, 'create_policy_version')
    result = boto_iot.create_policy_version(policyName=policy_ret['policyName'],
                                    policyDocument=policy_ret['policyDocument'],
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('create_policy_version')

def test_that_when_deleting_a_policy_version_succeeds_the_delete_policy_version_method_returns_true(boto_conn):
    '''
    tests True policy_version deleted.
    '''
    result = boto_iot.delete_policy_version(policyName='testpolicy',
                                    policyVersionId=1,
                                    **pytest.conn_parameters)

    assert result['deleted']

def test_that_when_deleting_a_policy_version_fails_the_delete_policy_version_method_returns_false(boto_conn):
    '''
    tests False policy_version not deleted.
    '''
    boto_conn.delete_policy_version.side_effect = exceptions.ClientError(error_content, 'delete_policy_version')
    result = boto_iot.delete_policy_version(policyName='testpolicy',
                                    policyVersionId=1,
                                    **pytest.conn_parameters)
    assert not result['deleted']

def test_that_when_describing_policy_version_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if policy_version exists
    '''
    boto_conn.get_policy_version.return_value = {'policy': policy_ret}

    result = boto_iot.describe_policy_version(policyName=policy_ret['policyName'],
                                    policyVersionId=1,
                                    **pytest.conn_parameters)

    assert result['policy']

def test_that_when_describing_policy_version_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters if policy_version does not exist
    '''
    boto_conn.get_policy_version.side_effect = not_found_error
    result = boto_iot.describe_policy_version(policyName=policy_ret['policyName'],
                                    policyVersionId=1,
                                    **pytest.conn_parameters)

    assert not result['policy']

def test_that_when_describing_policy_version_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.get_policy_version.side_effect = exceptions.ClientError(error_content, 'get_policy_version')
    result = boto_iot.describe_policy_version(policyName=policy_ret['policyName'],
                                    policyVersionId=1,
                                    **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_listing_policies_succeeds_the_list_policies_method_returns_true(boto_conn):
    '''
    tests True policies listed.
    '''
    boto_conn.list_policies.return_value = {'policies': [policy_ret]}
    result = boto_iot.list_policies(**pytest.conn_parameters)

    assert result['policies']

def test_that_when_listing_policy_fails_the_list_policy_method_returns_false(boto_conn):
    '''
    tests False no policy listed.
    '''
    boto_conn.list_policies.return_value = {'policies': []}
    result = boto_iot.list_policies(**pytest.conn_parameters)
    assert not result['policies']

def test_that_when_listing_policy_fails_the_list_policy_method_returns_error(boto_conn):
    '''
    tests False policy error.
    '''
    boto_conn.list_policies.side_effect = exceptions.ClientError(error_content, 'list_policies')
    result = boto_iot.list_policies(**pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('list_policies')

def test_that_when_listing_policy_versions_succeeds_the_list_policy_versions_method_returns_true(boto_conn):
    '''
    tests True policy versions listed.
    '''
    boto_conn.list_policy_versions.return_value = {'policyVersions': [policy_ret]}
    result = boto_iot.list_policy_versions(policyName='testpolicy',
                                           **pytest.conn_parameters)

    assert result['policyVersions']

def test_that_when_listing_policy_versions_fails_the_list_policy_versions_method_returns_false(boto_conn):
    '''
    tests False no policy versions listed.
    '''
    boto_conn.list_policy_versions.return_value = {'policyVersions': []}
    result = boto_iot.list_policy_versions(policyName='testpolicy',
                                           **pytest.conn_parameters)
    assert not result['policyVersions']

def test_that_when_listing_policy_versions_fails_the_list_policy_versions_method_returns_error(boto_conn):
    '''
    tests False policy versions error.
    '''
    boto_conn.list_policy_versions.side_effect = exceptions.ClientError(error_content, 'list_policy_versions')
    result = boto_iot.list_policy_versions(policyName='testpolicy',
                                           **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('list_policy_versions')

def test_that_when_setting_default_policy_version_succeeds_the_set_default_policy_version_method_returns_true(boto_conn):
    '''
    tests True policy version set.
    '''
    result = boto_iot.set_default_policy_version(policyName='testpolicy',
                                           policyVersionId=1,
                                           **pytest.conn_parameters)

    assert result['changed']

def test_that_when_set_default_policy_version_fails_the_set_default_policy_version_method_returns_error(boto_conn):
    '''
    tests False policy version error.
    '''
    boto_conn.set_default_policy_version.side_effect = \
                            exceptions.ClientError(error_content, 'set_default_policy_version')
    result = boto_iot.set_default_policy_version(policyName='testpolicy',
                                           policyVersionId=1,
                                           **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('set_default_policy_version')

def test_that_when_list_principal_policies_succeeds_the_list_principal_policies_method_returns_true(boto_conn):
    '''
    tests True policies listed.
    '''
    boto_conn.list_principal_policies.return_value = {'policies': [policy_ret]}
    result = boto_iot.list_principal_policies(principal='us-east-1:GUID-GUID-GUID',
                                           **pytest.conn_parameters)

    assert result['policies']

def test_that_when_list_principal_policies_fails_the_list_principal_policies_method_returns_error(boto_conn):
    '''
    tests False policy version error.
    '''
    boto_conn.list_principal_policies.side_effect = \
                            exceptions.ClientError(error_content, 'list_principal_policies')
    result = boto_iot.list_principal_policies(principal='us-east-1:GUID-GUID-GUID',
                                           **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('list_principal_policies')

def test_that_when_attach_principal_policy_succeeds_the_attach_principal_policy_method_returns_true(boto_conn):
    '''
    tests True policy attached.
    '''
    result = boto_iot.attach_principal_policy(policyName='testpolicy',
                                           principal='us-east-1:GUID-GUID-GUID',
                                           **pytest.conn_parameters)

    assert result['attached']

def test_that_when_attach_principal_policy_version_fails_the_attach_principal_policy_version_method_returns_error(boto_conn):
    '''
    tests False policy version error.
    '''
    boto_conn.attach_principal_policy.side_effect = \
                            exceptions.ClientError(error_content, 'attach_principal_policy')
    result = boto_iot.attach_principal_policy(policyName='testpolicy',
                                           principal='us-east-1:GUID-GUID-GUID',
                                           **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('attach_principal_policy')

def test_that_when_detach_principal_policy_succeeds_the_detach_principal_policy_method_returns_true(boto_conn):
    '''
    tests True policy detached.
    '''
    result = boto_iot.detach_principal_policy(policyName='testpolicy',
                                           principal='us-east-1:GUID-GUID-GUID',
                                           **pytest.conn_parameters)

    assert result['detached']

def test_that_when_detach_principal_policy_version_fails_the_detach_principal_policy_version_method_returns_error(boto_conn):
    '''
    tests False policy version error.
    '''
    boto_conn.detach_principal_policy.side_effect = \
                            exceptions.ClientError(error_content, 'detach_principal_policy')
    result = boto_iot.detach_principal_policy(policyName='testpolicy',
                                           principal='us-east-1:GUID-GUID-GUID',
                                           **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('detach_principal_policy')


def test_that_when_checking_if_a_topic_rule_exists_and_a_topic_rule_exists_the_topic_rule_exists_method_returns_true(boto_conn):
    '''
    Tests checking iot topic_rule existence when the iot topic_rule already exists
    '''
    boto_conn.get_topic_rule.return_value = {'rule': topic_rule_ret}
    result = boto_iot.topic_rule_exists(ruleName=topic_rule_ret['ruleName'],
                                        **pytest.conn_parameters)

    assert result['exists']

def test_that_when_checking_if_a_rule_exists_and_a_rule_does_not_exist_the_topic_rule_exists_method_returns_false(boto_conn):
    '''
    Tests checking iot rule existence when the iot rule does not exist
    '''
    boto_conn.get_topic_rule.side_effect = topic_rule_not_found_error
    result = boto_iot.topic_rule_exists(ruleName='mypolicy', **pytest.conn_parameters)

    assert not result['exists']

def test_that_when_checking_if_a_topic_rule_exists_and_boto3_returns_an_error_the_topic_rule_exists_method_returns_error(boto_conn):
    '''
    Tests checking iot topic_rule existence when boto returns an error
    '''
    boto_conn.get_topic_rule.side_effect = exceptions.ClientError(error_content, 'get_topic_rule')
    result = boto_iot.topic_rule_exists(ruleName='myrule', **pytest.conn_parameters)

    assert result.get('error', {}).get('message') == \
                                  error_message.format('get_topic_rule')

def test_that_when_creating_a_topic_rule_succeeds_the_create_topic_rule_method_returns_true(boto_conn):
    '''
    tests True topic_rule created.
    '''
    boto_conn.create_topic_rule.return_value = topic_rule_ret
    result = boto_iot.create_topic_rule(ruleName=topic_rule_ret['ruleName'],
                                    sql=topic_rule_ret['sql'],
                                    description=topic_rule_ret['description'],
                                    actions=topic_rule_ret['actions'],
                                    **pytest.conn_parameters)

    assert result['created']

def test_that_when_creating_a_topic_rule_fails_the_create_topic_rule_method_returns_error(boto_conn):
    '''
    tests False topic_rule not created.
    '''
    boto_conn.create_topic_rule.side_effect = exceptions.ClientError(error_content, 'create_topic_rule')
    result = boto_iot.create_topic_rule(ruleName=topic_rule_ret['ruleName'],
                                    sql=topic_rule_ret['sql'],
                                    description=topic_rule_ret['description'],
                                    actions=topic_rule_ret['actions'],
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('create_topic_rule')

def test_that_when_replacing_a_topic_rule_succeeds_the_replace_topic_rule_method_returns_true(boto_conn):
    '''
    tests True topic_rule replaced.
    '''
    boto_conn.replace_topic_rule.return_value = topic_rule_ret
    result = boto_iot.replace_topic_rule(ruleName=topic_rule_ret['ruleName'],
                                    sql=topic_rule_ret['sql'],
                                    description=topic_rule_ret['description'],
                                    actions=topic_rule_ret['actions'],
                                    **pytest.conn_parameters)

    assert result['replaced']

def test_that_when_replacing_a_topic_rule_fails_the_replace_topic_rule_method_returns_error(boto_conn):
    '''
    tests False topic_rule not replaced.
    '''
    boto_conn.replace_topic_rule.side_effect = exceptions.ClientError(error_content, 'replace_topic_rule')
    result = boto_iot.replace_topic_rule(ruleName=topic_rule_ret['ruleName'],
                                    sql=topic_rule_ret['sql'],
                                    description=topic_rule_ret['description'],
                                    actions=topic_rule_ret['actions'],
                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('replace_topic_rule')

def test_that_when_deleting_a_topic_rule_succeeds_the_delete_topic_rule_method_returns_true(boto_conn):
    '''
    tests True topic_rule deleted.
    '''
    result = boto_iot.delete_topic_rule(ruleName='testrule',
                                    **pytest.conn_parameters)

    assert result['deleted']

def test_that_when_deleting_a_topic_rule_fails_the_delete_topic_rule_method_returns_false(boto_conn):
    '''
    tests False topic_rule not deleted.
    '''
    boto_conn.delete_topic_rule.side_effect = exceptions.ClientError(error_content, 'delete_topic_rule')
    result = boto_iot.delete_topic_rule(ruleName='testrule',
                                    **pytest.conn_parameters)
    assert not result['deleted']

def test_that_when_describing_topic_rule_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if topic_rule exists
    '''
    boto_conn.get_topic_rule.return_value = {'rule': topic_rule_ret}

    result = boto_iot.describe_topic_rule(ruleName=topic_rule_ret['ruleName'],
                                          **pytest.conn_parameters)

    assert result['rule']

def test_that_when_describing_topic_rule_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.get_topic_rule.side_effect = exceptions.ClientError(error_content, 'get_topic_rule')
    result = boto_iot.describe_topic_rule(ruleName='testrule', **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_listing_topic_rules_succeeds_the_list_topic_rules_method_returns_true(boto_conn):
    '''
    tests True topic_rules listed.
    '''
    boto_conn.list_topic_rules.return_value = {'rules': [topic_rule_ret]}
    result = boto_iot.list_topic_rules(**pytest.conn_parameters)

    assert result['rules']

def test_that_when_listing_topic_rules_fails_the_list_topic_rules_method_returns_error(boto_conn):
    '''
    tests False policy error.
    '''
    boto_conn.list_topic_rules.side_effect = exceptions.ClientError(error_content, 'list_topic_rules')
    result = boto_iot.list_topic_rules(**pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('list_topic_rules')
