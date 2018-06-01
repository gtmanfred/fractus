# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging
import os
from tempfile import NamedTemporaryFile

# linux_distribution deprecated in py3.7
try:
    from platform import linux_distribution
except ImportError:
    from distro import linux_distribution

# Import Salt libs
from salt.exceptions import SaltInvocationError
import salt.utils.stringutils
from salt.ext import six

# Import Fractus Libs
import fractus.cloudmodules.boto_lambda as boto_lambda

# Import Testing libs
import pytest
from mock import MagicMock, patch

ON_SUSE = False
if 'SuSE' in linux_distribution(full_distribution_name=False):
    ON_SUSE = True

boto3 = pytest.importorskip('boto3', minversion='1.2.1')
botocore = pytest.importorskip('botocore', minversion='1.5.2')
exceptions = pytest.importorskip('botocore.exceptions')


error_message = 'An error occurred (101) when calling the {0} operation: Test-defined error'
error_content = {
    'Error': {
        'Code': 101,
        'Message': "Test-defined error"
    }
}
function_ret = dict(FunctionName='testfunction',
                    Runtime='python2.7',
                    Role=None,
                    Handler='handler',
                    Description='abcdefg',
                    Timeout=5,
                    MemorySize=128,
                    CodeSha256='abcdef',
                    CodeSize=199,
                    FunctionArn='arn:lambda:us-east-1:1234:Something',
                    LastModified='yes',
                    VpcConfig=None,
                    Environment=None)
alias_ret = dict(AliasArn='arn:lambda:us-east-1:1234:Something',
                 Name='testalias',
                 FunctionVersion='3',
                 Description='Alias description')
event_source_mapping_ret = dict(UUID='1234-1-123',
                                BatchSize=123,
                                EventSourceArn='arn:lambda:us-east-1:1234:Something',
                                FunctionArn='arn:lambda:us-east-1:1234:Something',
                                LastModified='yes',
                                LastProcessingResult='SUCCESS',
                                State='Enabled',
                                StateTransitionReason='Random')

log = logging.getLogger(__name__)


def setup_module():
    pytest.helpers.setup_loader({boto_lambda: {'__utils__': pytest.utils}})
    boto_lambda.__init__(pytest.opts)


class TempZipFile(object):

    def __enter__(self):
        with NamedTemporaryFile(
                suffix='.zip', prefix='salt_test_', delete=False) as tmp:
            to_write = '###\n'
            if six.PY3:
                to_write = salt.utils.stringutils.to_bytes(to_write)
            tmp.write(to_write)
            self.zipfile = tmp.name
        return self.zipfile

    def __exit__(boto_conn, type, value, traceback):
        os.remove(boto_conn.zipfile)


def test_that_when_checking_if_a_function_exists_and_a_function_exists_the_function_exists_method_returns_true(boto_conn):
    '''
    Tests checking lambda function existence when the lambda function already exists
    '''
    boto_conn.list_functions.return_value = {'Functions': [function_ret]}
    func_exists_result = boto_lambda.function_exists(
        FunctionName=function_ret['FunctionName'], **pytest.conn_parameters)

    assert func_exists_result['exists']

def test_that_when_checking_if_a_function_exists_and_a_function_does_not_exist_the_function_exists_method_returns_false(boto_conn):
    '''
    Tests checking lambda function existence when the lambda function does not exist
    '''
    boto_conn.list_functions.return_value = {'Functions': [function_ret]}
    func_exists_result = boto_lambda.function_exists(
        FunctionName='myfunc', **pytest.conn_parameters)

    assert not func_exists_result['exists']

def test_that_when_checking_if_a_function_exists_and_boto3_returns_an_error_the_function_exists_method_returns_error(boto_conn):
    '''
    Tests checking lambda function existence when boto returns an error
    '''
    boto_conn.list_functions.side_effect = exceptions.ClientError(
        error_content, 'list_functions')
    func_exists_result = boto_lambda.function_exists(
        FunctionName='myfunc', **pytest.conn_parameters)

    assert func_exists_result.get('error', {}).get(
        'message') == error_message.format('list_functions')

def test_that_when_creating_a_function_from_zipfile_succeeds_the_create_function_method_returns_true(boto_conn):
    '''
    tests True function created.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        with TempZipFile() as zipfile:
            boto_conn.create_function.return_value = function_ret
            lambda_creation_result = boto_lambda.create_function(
                FunctionName='testfunction',
                Runtime='python2.7',
                Role='myrole',
                Handler='file.method',
                ZipFile=zipfile,
                **pytest.conn_parameters)

    assert lambda_creation_result['created']

def test_that_when_creating_a_function_from_s3_succeeds_the_create_function_method_returns_true(boto_conn):
    '''
    tests True function created.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.create_function.return_value = function_ret
        lambda_creation_result = boto_lambda.create_function(
            FunctionName='testfunction',
            Runtime='python2.7',
            Role='myrole',
            Handler='file.method',
            S3Bucket='bucket',
            S3Key='key',
            **pytest.conn_parameters)

    assert lambda_creation_result['created']

def test_that_when_creating_a_function_without_code_raises_a_salt_invocation_error(boto_conn):
    '''
    tests Creating a function without code
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        with pytest.raises(SaltInvocationError) as excinfo:
            lambda_creation_result = boto_lambda.create_function(
                FunctionName='testfunction',
                Runtime='python2.7',
                Role='myrole',
                Handler='file.method',
                **pytest.conn_parameters)
    assert str(excinfo.value) == 'Either ZipFile must be specified, or S3Bucket and S3Key must be provided.'

def test_that_when_creating_a_function_with_zipfile_and_s3_raises_a_salt_invocation_error(boto_conn):
    '''
    tests Creating a function without code
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        with pytest.raises(SaltInvocationError) as excinfo:
            with TempZipFile() as zipfile:
                lambda_creation_result = boto_lambda.create_function(
                    FunctionName='testfunction',
                    Runtime='python2.7',
                    Role='myrole',
                    Handler='file.method',
                    ZipFile=zipfile,
                    S3Bucket='bucket',
                    S3Key='key',
                    **pytest.conn_parameters)
    assert str(excinfo.value) == 'Either ZipFile must be specified, or S3Bucket and S3Key must be provided.'

def test_that_when_creating_a_function_fails_the_create_function_method_returns_error(boto_conn):
    '''
    tests False function not created.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.create_function.side_effect = exceptions.ClientError(
            error_content, 'create_function')
        with TempZipFile() as zipfile:
            lambda_creation_result = boto_lambda.create_function(
                FunctionName='testfunction',
                Runtime='python2.7',
                Role='myrole',
                Handler='file.method',
                ZipFile=zipfile,
                **pytest.conn_parameters)
    assert lambda_creation_result.get('error', {}).get(
        'message') == error_message.format('create_function')

def test_that_when_deleting_a_function_succeeds_the_delete_function_method_returns_true(boto_conn):
    '''
    tests True function deleted.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_lambda.delete_function(FunctionName='testfunction',
                                             Qualifier=1,
                                             **pytest.conn_parameters)

    assert result['deleted']

def test_that_when_deleting_a_function_fails_the_delete_function_method_returns_false(boto_conn):
    '''
    tests False function not deleted.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.delete_function.side_effect = exceptions.ClientError(
            error_content, 'delete_function')
        result = boto_lambda.delete_function(FunctionName='testfunction',
                                             **pytest.conn_parameters)
    assert not result['deleted']

def test_that_when_describing_function_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if function exists
    '''
    boto_conn.list_functions.return_value = {'Functions': [function_ret]}

    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_lambda.describe_function(
            FunctionName=function_ret['FunctionName'], **pytest.conn_parameters)

    assert result == {'function': function_ret}

def test_that_when_describing_function_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters if function does not exist
    '''
    boto_conn.list_functions.return_value = {'Functions': []}
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        result = boto_lambda.describe_function(
            FunctionName='testfunction', **pytest.conn_parameters)

    assert not result['function']

def test_that_when_describing_lambda_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.list_functions.side_effect = exceptions.ClientError(
        error_content, 'list_functions')
    result = boto_lambda.describe_function(
        FunctionName='testfunction', **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_updating_a_function_succeeds_the_update_function_method_returns_true(boto_conn):
    '''
    tests True function updated.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.update_function_config.return_value = function_ret
        result = boto_lambda.update_function_config(
            FunctionName=function_ret['FunctionName'], Role='myrole', **pytest.conn_parameters)

    assert result['updated']

def test_that_when_updating_a_function_fails_the_update_function_method_returns_error(boto_conn):
    '''
    tests False function not updated.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.update_function_configuration.side_effect = exceptions.ClientError(
            error_content, 'update_function')
        result = boto_lambda.update_function_config(FunctionName='testfunction',
                                                    Role='myrole',
                                                    **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('update_function')

def test_that_when_updating_function_code_from_zipfile_succeeds_the_update_function_method_returns_true(boto_conn):
    '''
    tests True function updated.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        with TempZipFile() as zipfile:
            boto_conn.update_function_code.return_value = function_ret
            result = boto_lambda.update_function_code(
                FunctionName=function_ret['FunctionName'],
                ZipFile=zipfile, **pytest.conn_parameters)

    assert result['updated']

def test_that_when_updating_function_code_from_s3_succeeds_the_update_function_method_returns_true(boto_conn):
    '''
    tests True function updated.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.update_function_code.return_value = function_ret
        result = boto_lambda.update_function_code(
            FunctionName='testfunction',
            S3Bucket='bucket',
            S3Key='key',
            **pytest.conn_parameters)

    assert result['updated']

def test_that_when_updating_function_code_without_code_raises_a_salt_invocation_error(boto_conn):
    '''
    tests Creating a function without code
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        with pytest.raises(SaltInvocationError) as excinfo:
            result = boto_lambda.update_function_code(
                FunctionName='testfunction',
                **pytest.conn_parameters)
    assert str(excinfo.value) == 'Either ZipFile must be specified, or S3Bucket and S3Key must be provided.'

def test_that_when_updating_function_code_fails_the_update_function_method_returns_error(boto_conn):
    '''
    tests False function not updated.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.update_function_code.side_effect = exceptions.ClientError(
            error_content, 'update_function_code')
        result = boto_lambda.update_function_code(
            FunctionName='testfunction',
            S3Bucket='bucket',
            S3Key='key',
            **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('update_function_code')

def test_that_when_listing_function_versions_succeeds_the_list_function_versions_method_returns_true(boto_conn):
    '''
    tests True function versions listed.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.list_versions_by_function.return_value = {
            'Versions': [function_ret]}
        result = boto_lambda.list_function_versions(
            FunctionName='testfunction',
            **pytest.conn_parameters)

    assert result['Versions']

def test_that_when_listing_function_versions_fails_the_list_function_versions_method_returns_false(boto_conn):
    '''
    tests False no function versions listed.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.list_versions_by_function.return_value = {'Versions': []}
        result = boto_lambda.list_function_versions(
            FunctionName='testfunction',
            **pytest.conn_parameters)
    assert not result['Versions']

def test_that_when_listing_function_versions_fails_the_list_function_versions_method_returns_error(boto_conn):
    '''
    tests False function versions error.
    '''
    with patch.dict(boto_lambda.__salt__, {'boto_iam.get_account_id': MagicMock(return_value='1234')}):
        boto_conn.list_versions_by_function.side_effect = exceptions.ClientError(
            error_content, 'list_versions_by_function')
        result = boto_lambda.list_function_versions(
            FunctionName='testfunction',
            **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('list_versions_by_function')


def test_that_when_creating_an_alias_succeeds_the_create_alias_method_returns_true(boto_conn):
    '''
    tests True alias created.
    '''
    boto_conn.create_alias.return_value = alias_ret
    result = boto_lambda.create_alias(FunctionName='testfunction',
                                      Name=alias_ret['Name'],
                                      FunctionVersion=alias_ret[
                                          'FunctionVersion'],
                                      **pytest.conn_parameters)

    assert result['created']

def test_that_when_creating_an_alias_fails_the_create_alias_method_returns_error(boto_conn):
    '''
    tests False alias not created.
    '''
    boto_conn.create_alias.side_effect = exceptions.ClientError(
        error_content, 'create_alias')
    result = boto_lambda.create_alias(FunctionName='testfunction',
                                      Name=alias_ret['Name'],
                                      FunctionVersion=alias_ret[
                                          'FunctionVersion'],
                                      **pytest.conn_parameters)
    assert result.get('error', {}).get(
        'message') == error_message.format('create_alias')

def test_that_when_deleting_an_alias_succeeds_the_delete_alias_method_returns_true(boto_conn):
    '''
    tests True alias deleted.
    '''
    result = boto_lambda.delete_alias(FunctionName='testfunction',
                                      Name=alias_ret['Name'],
                                      **pytest.conn_parameters)

    assert result['deleted']

def test_that_when_deleting_an_alias_fails_the_delete_alias_method_returns_false(boto_conn):
    '''
    tests False alias not deleted.
    '''
    boto_conn.delete_alias.side_effect = exceptions.ClientError(
        error_content, 'delete_alias')
    result = boto_lambda.delete_alias(FunctionName='testfunction',
                                      Name=alias_ret['Name'],
                                      **pytest.conn_parameters)
    assert not result['deleted']

def test_that_when_checking_if_an_alias_exists_and_the_alias_exists_the_alias_exists_method_returns_true(boto_conn):
    '''
    Tests checking lambda alias existence when the lambda alias already exists
    '''
    boto_conn.list_aliases.return_value = {'Aliases': [alias_ret]}
    result = boto_lambda.alias_exists(FunctionName='testfunction',
                                      Name=alias_ret['Name'],
                                      **pytest.conn_parameters)
    assert result['exists']

def test_that_when_checking_if_an_alias_exists_and_the_alias_does_not_exist_the_alias_exists_method_returns_false(boto_conn):
    '''
    Tests checking lambda alias existence when the lambda alias does not exist
    '''
    boto_conn.list_aliases.return_value = {'Aliases': [alias_ret]}
    result = boto_lambda.alias_exists(FunctionName='testfunction',
                                      Name='otheralias',
                                      **pytest.conn_parameters)

    assert not result['exists']

def test_that_when_checking_if_an_alias_exists_and_boto3_returns_an_error_the_alias_exists_method_returns_error(boto_conn):
    '''
    Tests checking lambda alias existence when boto returns an error
    '''
    boto_conn.list_aliases.side_effect = exceptions.ClientError(
        error_content, 'list_aliases')
    result = boto_lambda.alias_exists(FunctionName='testfunction',
                                      Name=alias_ret['Name'],
                                      **pytest.conn_parameters)

    assert result.get('error', {}).get(
        'message') == error_message.format('list_aliases')

def test_that_when_describing_alias_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if alias exists
    '''
    boto_conn.list_aliases.return_value = {'Aliases': [alias_ret]}

    result = boto_lambda.describe_alias(FunctionName='testfunction',
                                        Name=alias_ret['Name'],
                                        **pytest.conn_parameters)

    assert result == {'alias': alias_ret}

def test_that_when_describing_alias_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters if alias does not exist
    '''
    boto_conn.list_aliases.return_value = {'Aliases': [alias_ret]}
    result = boto_lambda.describe_alias(FunctionName='testfunction',
                                        Name='othername',
                                        **pytest.conn_parameters)

    assert not result['alias']

def test_that_when_describing_lambda_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.list_aliases.side_effect = exceptions.ClientError(
        error_content, 'list_aliases')
    result = boto_lambda.describe_alias(FunctionName='testfunction',
                                        Name=alias_ret['Name'],
                                        **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_updating_an_alias_succeeds_the_update_alias_method_returns_true(boto_conn):
    '''
    tests True alias updated.
    '''
    boto_conn.update_alias.return_value = alias_ret
    result = boto_lambda.update_alias(FunctionName='testfunctoin',
                                      Name=alias_ret['Name'],
                                      Description=alias_ret['Description'],
                                      **pytest.conn_parameters)

    assert result['updated']

def test_that_when_updating_an_alias_fails_the_update_alias_method_returns_error(boto_conn):
    '''
    tests False alias not updated.
    '''
    boto_conn.update_alias.side_effect = exceptions.ClientError(
        error_content, 'update_alias')
    result = boto_lambda.update_alias(FunctionName='testfunction',
                                      Name=alias_ret['Name'],
                                      **pytest.conn_parameters)
    assert result.get('error', {}).get(
        'message') == error_message.format('update_alias')


def test_that_when_creating_a_mapping_succeeds_the_create_event_source_mapping_method_returns_true(boto_conn):
    '''
    tests True mapping created.
    '''
    boto_conn.create_event_source_mapping.return_value = event_source_mapping_ret
    result = boto_lambda.create_event_source_mapping(
        EventSourceArn=event_source_mapping_ret['EventSourceArn'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        StartingPosition='LATEST',
        **pytest.conn_parameters)

    assert result['created']

def test_that_when_creating_an_event_source_mapping_fails_the_create_event_source_mapping_method_returns_error(boto_conn):
    '''
    tests False mapping not created.
    '''
    boto_conn.create_event_source_mapping.side_effect = exceptions.ClientError(
        error_content, 'create_event_source_mapping')
    result = boto_lambda.create_event_source_mapping(
        EventSourceArn=event_source_mapping_ret['EventSourceArn'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        StartingPosition='LATEST',
        **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('create_event_source_mapping')

def test_that_when_listing_mapping_ids_succeeds_the_get_event_source_mapping_ids_method_returns_true(boto_conn):
    '''
    tests True mapping ids listed.
    '''
    boto_conn.list_event_source_mappings.return_value = {
        'EventSourceMappings': [event_source_mapping_ret]}
    result = boto_lambda.get_event_source_mapping_ids(
        EventSourceArn=event_source_mapping_ret['EventSourceArn'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        **pytest.conn_parameters)

    assert result

def test_that_when_listing_event_source_mapping_ids_fails_the_get_event_source_mapping_ids_versions_method_returns_false(boto_conn):
    '''
    tests False no mapping ids listed.
    '''
    boto_conn.list_event_source_mappings.return_value = {
        'EventSourceMappings': []}
    result = boto_lambda.get_event_source_mapping_ids(
        EventSourceArn=event_source_mapping_ret['EventSourceArn'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        **pytest.conn_parameters)
    assert not result

def test_that_when_listing_event_source_mapping_ids_fails_the_get_event_source_mapping_ids_method_returns_error(boto_conn):
    '''
    tests False mapping ids error.
    '''
    boto_conn.list_event_source_mappings.side_effect = exceptions.ClientError(
        error_content, 'list_event_source_mappings')
    result = boto_lambda.get_event_source_mapping_ids(
        EventSourceArn=event_source_mapping_ret['EventSourceArn'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('list_event_source_mappings')

def test_that_when_deleting_an_event_source_mapping_by_UUID_succeeds_the_delete_event_source_mapping_method_returns_true(boto_conn):
    '''
    tests True mapping deleted.
    '''
    result = boto_lambda.delete_event_source_mapping(
        UUID=event_source_mapping_ret['UUID'],
        **pytest.conn_parameters)
    assert result['deleted']

@pytest.mark.skip('This appears to leak memory and crash the unit test suite')
def test_that_when_deleting_an_event_source_mapping_by_name_succeeds_the_delete_event_source_mapping_method_returns_true(boto_conn):
    '''
    tests True mapping deleted.
    '''
    boto_conn.list_event_source_mappings.return_value = {
        'EventSourceMappings': [event_source_mapping_ret]}
    result = boto_lambda.delete_event_source_mapping(
        EventSourceArn=event_source_mapping_ret['EventSourceArn'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        **pytest.conn_parameters)
    assert result['deleted']

def test_that_when_deleting_an_event_source_mapping_without_identifier_the_delete_event_source_mapping_method_raises_saltinvocationexception(boto_conn):
    '''
    tests Deleting a mapping without identifier
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        result = boto_lambda.delete_event_source_mapping(**pytest.conn_parameters)
    assert str(excinfo.value) == 'Either UUID must be specified, or EventSourceArn and FunctionName must be provided.'

def test_that_when_deleting_an_event_source_mapping_fails_the_delete_event_source_mapping_method_returns_false(boto_conn):
    '''
    tests False mapping not deleted.
    '''
    boto_conn.delete_event_source_mapping.side_effect = exceptions.ClientError(
        error_content, 'delete_event_source_mapping')
    result = boto_lambda.delete_event_source_mapping(UUID=event_source_mapping_ret['UUID'],
                                                     **pytest.conn_parameters)
    assert not result['deleted']

def test_that_when_checking_if_an_event_source_mapping_exists_and_the_event_source_mapping_exists_the_event_source_mapping_exists_method_returns_true(boto_conn):
    '''
    Tests checking lambda event_source_mapping existence when the lambda
    event_source_mapping already exists
    '''
    boto_conn.get_event_source_mapping.return_value = event_source_mapping_ret
    result = boto_lambda.event_source_mapping_exists(
        UUID=event_source_mapping_ret['UUID'],
        **pytest.conn_parameters)
    assert result['exists']

def test_that_when_checking_if_an_event_source_mapping_exists_and_the_event_source_mapping_does_not_exist_the_event_source_mapping_exists_method_returns_false(boto_conn):
    '''
    Tests checking lambda event_source_mapping existence when the lambda
    event_source_mapping does not exist
    '''
    boto_conn.get_event_source_mapping.return_value = None
    result = boto_lambda.event_source_mapping_exists(
        UUID='other_UUID',
        **pytest.conn_parameters)
    assert not result['exists']

def test_that_when_checking_if_an_event_source_mapping_exists_and_boto3_returns_an_error_the_event_source_mapping_exists_method_returns_error(boto_conn):
    '''
    Tests checking lambda event_source_mapping existence when boto returns an error
    '''
    boto_conn.get_event_source_mapping.side_effect = exceptions.ClientError(
        error_content, 'list_event_source_mappings')
    result = boto_lambda.event_source_mapping_exists(
        UUID=event_source_mapping_ret['UUID'],
        **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('list_event_source_mappings')

def test_that_when_describing_event_source_mapping_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters if event_source_mapping exists
    '''
    boto_conn.get_event_source_mapping.return_value = event_source_mapping_ret
    result = boto_lambda.describe_event_source_mapping(
        UUID=event_source_mapping_ret['UUID'],
        **pytest.conn_parameters)
    assert result == {'event_source_mapping': event_source_mapping_ret}

def test_that_when_describing_event_source_mapping_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters if event_source_mapping does not exist
    '''
    boto_conn.get_event_source_mapping.return_value = None
    result = boto_lambda.describe_event_source_mapping(
        UUID=event_source_mapping_ret['UUID'],
        **pytest.conn_parameters)
    assert not result['event_source_mapping']

def test_that_when_describing_event_source_mapping_on_client_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    boto_conn.get_event_source_mapping.side_effect = exceptions.ClientError(
        error_content, 'get_event_source_mapping')
    result = boto_lambda.describe_event_source_mapping(
        UUID=event_source_mapping_ret['UUID'],
        **pytest.conn_parameters)
    assert 'error' in result

def test_that_when_updating_an_event_source_mapping_succeeds_the_update_event_source_mapping_method_returns_true(boto_conn):
    '''
    tests True event_source_mapping updated.
    '''
    boto_conn.update_event_source_mapping.return_value = event_source_mapping_ret
    result = boto_lambda.update_event_source_mapping(
        UUID=event_source_mapping_ret['UUID'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        **pytest.conn_parameters)

    assert result['updated']

def test_that_when_updating_an_event_source_mapping_fails_the_update_event_source_mapping_method_returns_error(boto_conn):
    '''
    tests False event_source_mapping not updated.
    '''
    boto_conn.update_event_source_mapping.side_effect = exceptions.ClientError(
        error_content, 'update_event_source_mapping')
    result = boto_lambda.update_event_source_mapping(
        UUID=event_source_mapping_ret['UUID'],
        FunctionName=event_source_mapping_ret['FunctionArn'],
        **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('update_event_source_mapping')
