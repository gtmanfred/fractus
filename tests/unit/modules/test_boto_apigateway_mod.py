# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import datetime
import logging

# Import Salt libs
from salt.ext.six.moves import range, zip

# Import Factus libs
import fractus.cloudmodules.boto_apigateway as boto_apigateway

# Import Testing Libs
import pytest


boto3 = pytest.importorskip('boto3', minversion='1.2.1')
botocore = pytest.importorskip('botocore', minversion='1.4.49')
exceptions = pytest.importorskip('botocore.exceptions')

error_message = 'An error occurred (101) when calling the {0} operation: Test-defined error'
error_content = {
  'Error': {
    'Code': 101,
    'Message': "Test-defined error"
  }
}

api_key_ret = {
            u'description': u'test-lambda-api-key', u'enabled': True,
            u'stageKeys': [u'123yd1l123/test'],
            u'lastUpdatedDate': datetime.datetime(2015, 11, 4, 19, 22, 18),
            u'createdDate': datetime.datetime(2015, 11, 4, 19, 21, 7),
            u'id': u'88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
            u'name': u'test-salt-key',
            'ResponseMetadata': {'HTTPStatusCode': 200,
                                 'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}

api_model_error_schema = u'{"properties":{"code":{"type":"integer","format":"int32"},"message":{"type":"string"},"fields":{"type":"string"}},"definitions":{}}'
api_model_ret = {
            u'contentType': u'application/json',
            u'name': u'Error',
            u'description': u'Error Model',
            u'id': u'iltqcb',
            u'schema': api_model_error_schema,
            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}

api_resources_ret = {
            u'items': [{u'id': u'hhg2t8f4h9',
                        u'path': u'/'},
                       {u'id': u'isr8q2',
                        u'parentId': u'hhg2t8f4h9',
                        u'path': u'/api',
                        u'pathPart': u'api'},
                       {u'id': u'5pvx7w',
                        u'parentId': 'isr8q2',
                        u'path': u'/api/users',
                        u'pathPart': u'users',
                        u'resourceMethods': {u'OPTIONS': {},
                                             u'POST': {}}}],
            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}

api_create_resource_ret = {
            u'id': u'123abc',
            u'parentId': u'hhg2t8f4h9',
            u'path': u'/api3',
            u'pathPart': u'api3',
            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}

usage_plan1 = dict(
    id='plan1_id',
    name='plan1_name',
    description='plan1_desc',
    apiStages=[],
    throttle=dict(
        burstLimit=123,
        rateLimit=123.0
    ),
    quota=dict(
        limit=123,
        offset=123,
        period='DAY'
    )
)
usage_plan2 = dict(
    id='plan2_id',
    name='plan2_name',
    description='plan2_desc',
    apiStages=[],
    throttle=dict(
        burstLimit=123,
        rateLimit=123.0
    ),
    quota=dict(
        limit=123,
        offset=123,
        period='DAY'
    )
)
usage_plan1b = dict(
    id='another_plan1_id',
    name='plan1_name',
    description='another_plan1_desc',
    apiStages=[],
    throttle=dict(
        burstLimit=123,
        rateLimit=123.0
    ),
    quota=dict(
        limit=123,
        offset=123,
        period='DAY'
    )
)
usage_plans_ret = dict(
    items=[
        usage_plan1, usage_plan2, usage_plan1b
    ]
)

log = logging.getLogger(__name__)


def setup_module():
    pytest.helpers.setup_loader({
        boto_apigateway: {
            '__opts__': pytest.opts,
            '__utils__': pytest.utils,
        }
    })
    boto_apigateway.__init__(pytest.opts)


def _diff_list_dicts(listdict1, listdict2, sortkey):
    '''
    Compares the two list of dictionaries to ensure they have same content.  Returns True
    if there is difference, else False
    '''
    if len(listdict1) != len(listdict2):
        return True

    listdict1_sorted = sorted(listdict1, key=lambda x: x[sortkey])
    listdict2_sorted = sorted(listdict2, key=lambda x: x[sortkey])
    for item1, item2 in zip(listdict1_sorted, listdict2_sorted):
        if len(set(item1) & set(item2)) != len(set(item2)):
            return True
    return False


def test_that_when_checking_if_a_rest_api_exists_and_a_rest_api_exists_the_api_exists_method_returns_true(boto_conn):
    '''
    Tests checking an apigateway rest api existence when api's name exists
    '''
    boto_conn.get_rest_apis.return_value = {'items': [{'name': 'myapi', 'id': '1234def'}]}
    api_exists_result = boto_apigateway.api_exists(name='myapi', **pytest.conn_parameters)

    assert api_exists_result['exists']

def test_that_when_checking_if_a_rest_api_exists_and_multiple_rest_api_exist_the_api_exists_method_returns_true(boto_conn):
    '''
    Tests checking an apigateway rest api existence when multiple api's with same name exists
    '''
    boto_conn.get_rest_apis.return_value = {'items': [{'name': 'myapi', 'id': '1234abc'},
                                                      {'name': 'myapi', 'id': '1234def'}]}
    api_exists_result = boto_apigateway.api_exists(name='myapi', **pytest.conn_parameters)
    assert api_exists_result['exists']

def test_that_when_checking_if_a_rest_api_exists_and_no_rest_api_exists_the_api_exists_method_returns_false(boto_conn):
    '''
    Tests checking an apigateway rest api existence when no matching rest api name exists
    '''
    boto_conn.get_rest_apis.return_value = {'items': [{'name': 'myapi', 'id': '1234abc'},
                                                      {'name': 'myapi', 'id': '1234def'}]}
    api_exists_result = boto_apigateway.api_exists(name='myapi123', **pytest.conn_parameters)
    assert not api_exists_result['exists']

def test_that_when_describing_rest_apis_and_no_name_given_the_describe_apis_method_returns_list_of_all_rest_apis(boto_conn):
    '''
    Tests that all rest apis defined for a region is returned
    '''
    boto_conn.get_rest_apis.return_value = {u'items': [{u'description': u'A sample API that uses a petstore as an example to demonstrate features in the swagger-2.0 specification',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                                        u'id': u'2ut6i4vyle',
                                                        u'name': u'Swagger Petstore'},
                                                       {u'description': u'testingabcd',
                                                        u'createdDate': datetime.datetime(2015, 12, 3, 21, 57, 58),
                                                        u'id': u'g41ls77hz0',
                                                        u'name': u'testingabc'},
                                                       {u'description': u'a simple food delivery service test',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 23, 57, 28),
                                                        u'id': u'h7pbwydho9',
                                                        u'name': u'Food Delivery Service'},
                                                       {u'description': u'Created by AWS Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 17, 55, 41),
                                                        u'id': u'i2yyd1ldvj',
                                                        u'name': u'LambdaMicroservice'},
                                                       {u'description': u'cloud tap service with combination of API GW and Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 22, 3, 18),
                                                        u'id': u'rm06h9oac4',
                                                        u'name': u'API Gateway Cloudtap Service'},
                                                       {u'description': u'testing1234',
                                                        u'createdDate': datetime.datetime(2015, 12, 2, 19, 51, 44),
                                                        u'id': u'vtir6ssxvd',
                                                        u'name': u'testing123'}],
                                            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    items = boto_conn.get_rest_apis.return_value['items']
    get_apis_result = boto_apigateway.describe_apis(**pytest.conn_parameters)
    items_dt = [boto_apigateway._convert_datetime_str(item) for item in items]
    apis = get_apis_result.get('restapi')

    diff = _diff_list_dicts(apis, items_dt, 'id')

    assert apis
    assert len(apis) == len(items)
    assert not diff

def test_that_when_describing_rest_apis_and_name_is_testing123_the_describe_apis_method_returns_list_of_two_rest_apis(boto_conn):
    '''
    Tests that exactly 2 apis are returned matching 'testing123'
    '''
    boto_conn.get_rest_apis.return_value = {u'items': [{u'description': u'A sample API that uses a petstore as an example to demonstrate features in the swagger-2.0 specification',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                                        u'id': u'2ut6i4vyle',
                                                        u'name': u'Swagger Petstore'},
                                                       {u'description': u'testingabcd',
                                                        u'createdDate': datetime.datetime(2015, 12, 3, 21, 57, 58),
                                                        u'id': u'g41ls77hz0',
                                                        u'name': u'testing123'},
                                                       {u'description': u'a simple food delivery service test',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 23, 57, 28),
                                                        u'id': u'h7pbwydho9',
                                                        u'name': u'Food Delivery Service'},
                                                       {u'description': u'Created by AWS Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 17, 55, 41),
                                                        u'id': u'i2yyd1ldvj',
                                                        u'name': u'LambdaMicroservice'},
                                                       {u'description': u'cloud tap service with combination of API GW and Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 22, 3, 18),
                                                        u'id': u'rm06h9oac4',
                                                        u'name': u'API Gateway Cloudtap Service'},
                                                       {u'description': u'testing1234',
                                                        u'createdDate': datetime.datetime(2015, 12, 2, 19, 51, 44),
                                                        u'id': u'vtir6ssxvd',
                                                        u'name': u'testing123'}],
                                            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    expected_items = [{u'description': u'testingabcd', u'createdDate': datetime.datetime(2015, 12, 3, 21, 57, 58),
                       u'id': u'g41ls77hz0', u'name': u'testing123'},
                      {u'description': u'testing1234', u'createdDate': datetime.datetime(2015, 12, 2, 19, 51, 44),
                       u'id': u'vtir6ssxvd', u'name': u'testing123'}]

    get_apis_result = boto_apigateway.describe_apis(name='testing123', **pytest.conn_parameters)
    expected_items_dt = [boto_apigateway._convert_datetime_str(item) for item in expected_items]
    apis = get_apis_result.get('restapi')
    diff = _diff_list_dicts(apis, expected_items_dt, 'id')

    assert apis
    assert diff is False

def test_that_when_describing_rest_apis_and_name_is_testing123_the_describe_apis_method_returns_no_matching_items(boto_conn):
    '''
    Tests that no apis are returned matching 'testing123'
    '''
    boto_conn.get_rest_apis.return_value = {u'items': [{u'description': u'A sample API that uses a petstore as an example to demonstrate features in the swagger-2.0 specification',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                                        u'id': u'2ut6i4vyle',
                                                        u'name': u'Swagger Petstore'},
                                                       {u'description': u'a simple food delivery service test',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 23, 57, 28),
                                                        u'id': u'h7pbwydho9',
                                                        u'name': u'Food Delivery Service'},
                                                       {u'description': u'Created by AWS Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 17, 55, 41),
                                                        u'id': u'i2yyd1ldvj',
                                                        u'name': u'LambdaMicroservice'},
                                                       {u'description': u'cloud tap service with combination of API GW and Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 22, 3, 18),
                                                        u'id': u'rm06h9oac4',
                                                        u'name': u'API Gateway Cloudtap Service'}],
                                            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    get_apis_result = boto_apigateway.describe_apis(name='testing123', **pytest.conn_parameters)
    apis = get_apis_result.get('restapi')
    assert not apis

def test_that_when_creating_a_rest_api_succeeds_the_create_api_method_returns_true(boto_conn):
    '''
    test True if rest api is created
    '''
    created_date = datetime.datetime.now()
    assigned_api_id = 'created_api_id'
    boto_conn.create_rest_api.return_value = {u'description': u'unit-testing1234',
                                              u'createdDate': created_date,
                                              u'id': assigned_api_id,
                                              u'name': u'unit-testing123',
                                              'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}

    create_api_result = boto_apigateway.create_api(name='unit-testing123', description='unit-testing1234', **pytest.conn_parameters)
    api = create_api_result.get('restapi')
    assert create_api_result.get('created')
    assert api
    assert api['id'] == assigned_api_id
    assert api['createdDate'] == '{0}'.format(created_date)
    assert api['name'] == 'unit-testing123'
    assert api['description'] == 'unit-testing1234'

def test_that_when_creating_a_rest_api_fails_the_create_api_method_returns_error(boto_conn):
    '''
    test True for rest api creation error.
    '''
    boto_conn.create_rest_api.side_effect = exceptions.ClientError(error_content, 'create_rest_api')
    create_api_result = boto_apigateway.create_api(name='unit-testing123', description='unit-testing1234', **pytest.conn_parameters)
    api = create_api_result.get('restapi')
    assert create_api_result.get('error').get('message') == error_message.format('create_rest_api')

def test_that_when_deleting_rest_apis_and_name_is_testing123_matching_two_apis_the_delete_api_method_returns_delete_count_of_two(boto_conn):
    '''
    test True if the deleted count for "testing123" api is 2.
    '''
    boto_conn.get_rest_apis.return_value = {u'items': [{u'description': u'A sample API that uses a petstore as an example to demonstrate features in the swagger-2.0 specification',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                                        u'id': u'2ut6i4vyle',
                                                        u'name': u'Swagger Petstore'},
                                                       {u'description': u'testingabcd',
                                                        u'createdDate': datetime.datetime(2015, 12, 3, 21, 57, 58),
                                                        u'id': u'g41ls77hz0',
                                                        u'name': u'testing123'},
                                                       {u'description': u'a simple food delivery service test',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 23, 57, 28),
                                                        u'id': u'h7pbwydho9',
                                                        u'name': u'Food Delivery Service'},
                                                       {u'description': u'Created by AWS Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 4, 17, 55, 41),
                                                        u'id': u'i2yyd1ldvj',
                                                        u'name': u'LambdaMicroservice'},
                                                       {u'description': u'cloud tap service with combination of API GW and Lambda',
                                                        u'createdDate': datetime.datetime(2015, 11, 17, 22, 3, 18),
                                                        u'id': u'rm06h9oac4',
                                                        u'name': u'API Gateway Cloudtap Service'},
                                                       {u'description': u'testing1234',
                                                        u'createdDate': datetime.datetime(2015, 12, 2, 19, 51, 44),
                                                        u'id': u'vtir6ssxvd',
                                                        u'name': u'testing123'}],
                                            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    boto_conn.delete_rest_api.return_value = None
    delete_api_result = boto_apigateway.delete_api(name='testing123', **pytest.conn_parameters)

    assert delete_api_result.get('deleted')
    assert delete_api_result.get('count') == 2

def test_that_when_deleting_rest_apis_and_name_given_provides_no_match_the_delete_api_method_returns_false(boto_conn):
    '''
    Test that the given api name doesn't exists, and delete_api should return deleted status of False
    '''
    boto_conn.get_rest_apis.return_value = {u'items': [{u'description': u'testing1234',
                                                        u'createdDate': datetime.datetime(2015, 12, 2, 19, 51, 44),
                                                        u'id': u'vtir6ssxvd',
                                                        u'name': u'testing1234'}],
                                            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    boto_conn.delete_rest_api.return_value = None
    delete_api_result = boto_apigateway.delete_api(name='testing123', **pytest.conn_parameters)

    assert not delete_api_result.get('deleted')

def test_that_describing_api_keys_the_describe_api_keys_method_returns_all_api_keys(boto_conn):
    '''
    tests True if all api_keys are returned.
    '''
    boto_conn.get_api_keys.return_value = {
        u'items': [{u'description': u'test-lambda-api-key', u'enabled': True,
                    u'stageKeys': [u'123yd1l123/test'],
                    u'lastUpdatedDate': datetime.datetime(2015, 11, 4, 19, 22, 18),
                    u'createdDate': datetime.datetime(2015, 11, 4, 19, 21, 7),
                    u'id': u'88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                    u'name': u'test-salt-key'},
                   {u'description': u'testing_salt_123', u'enabled': True,
                    u'stageKeys': [],
                    u'lastUpdatedDate': datetime.datetime(2015, 12, 5, 0, 14, 49),
                    u'createdDate': datetime.datetime(2015, 12, 4, 22, 29, 33),
                    u'id': u'999999989b8cNSp4505pL6OgDe3oW7oY29Z3eIZ4',
                    u'name': u'testing_salt'}],
        'ResponseMetadata': {'HTTPStatusCode': 200,
                             'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}

    items = boto_conn.get_api_keys.return_value['items']
    get_api_keys_result = boto_apigateway.describe_api_keys(**pytest.conn_parameters)
    items_dt = [boto_apigateway._convert_datetime_str(item) for item in items]
    api_keys = get_api_keys_result.get('apiKeys')

    diff = False
    if len(api_keys) != len(items):
        diff = True
    else:
        # compare individual items.
        diff = _diff_list_dicts(api_keys, items_dt, 'id')

    assert api_keys
    assert diff is False

def test_that_describing_api_keys_fails_the_desribe_api_keys_method_returns_error(boto_conn):
    '''
    test True for describe api keys error.
    '''
    boto_conn.get_api_keys.side_effect = exceptions.ClientError(error_content, 'get_api_keys')
    result = boto_apigateway.describe_api_keys(**pytest.conn_parameters)
    assert result.get('error', {}).get('message') == error_message.format('get_api_keys')

def test_that_describing_an_api_key_the_describe_api_key_method_returns_matching_api_key(boto_conn):
    '''
    tests True if the key is found.
    '''
    boto_conn.get_api_key.return_value = api_key_ret
    result = boto_apigateway.describe_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                              **pytest.conn_parameters)
    assert result.get('apiKey', {}).get('id') == boto_conn.get_api_key.return_value.get('id')

def test_that_describing_an_api_key_that_does_not_exists_the_desribe_api_key_method_returns_error(boto_conn):
    '''
    test True for error being thrown.
    '''
    boto_conn.get_api_key.side_effect = exceptions.ClientError(error_content, 'get_api_keys')
    result = boto_apigateway.describe_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                              **pytest.conn_parameters)
    assert result.get('error', {}).get('message') == \
                     error_message.format('get_api_keys')

def test_that_when_creating_an_api_key_succeeds_the_create_api_key_method_returns_true(boto_conn):
    '''
    tests that we can successfully create an api key and the createDat and lastUpdateDate are
    converted to string
    '''
    now = datetime.datetime.now()
    boto_conn.create_api_key.return_value = {
        u'description': u'test-lambda-api-key', u'enabled': True,
        u'stageKeys': [u'123yd1l123/test'],
        u'lastUpdatedDate': now,
        u'createdDate': now,
        u'id': u'88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
        u'name': u'test-salt-key',
        'ResponseMetadata': {'HTTPStatusCode': 200,
                             'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}

    create_api_key_result = boto_apigateway.create_api_key('test-salt-key', 'test-lambda-api-key', **pytest.conn_parameters)
    api_key = create_api_key_result.get('apiKey')
    now_str = '{0}'.format(now)

    assert create_api_key_result.get('created')
    assert api_key.get('lastUpdatedDate') == now_str
    assert api_key.get('createdDate') == now_str

def test_that_when_creating_an_api_key_fails_the_create_api_key_method_returns_error(boto_conn):
    '''
    tests that we properly handle errors when create an api key fails.
    '''

    boto_conn.create_api_key.side_effect = exceptions.ClientError(error_content, 'create_api_key')
    create_api_key_result = boto_apigateway.create_api_key('test-salt-key', 'unit-testing1234')
    api_key = create_api_key_result.get('apiKey')

    assert not api_key
    assert create_api_key_result.get('created') is False
    assert create_api_key_result.get('error').get('message') == error_message.format('create_api_key')

def test_that_when_deleting_an_api_key_that_exists_the_delete_api_key_method_returns_true(boto_conn):
    '''
    test True if the api key is successfully deleted.
    '''
    boto_conn.delete_api_key.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.delete_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2', **pytest.conn_parameters)

    assert result.get('deleted')

def test_that_when_deleting_an_api_key_that_does_not_exist_the_delete_api_key_method_returns_false(boto_conn):
    '''
    Test that the given api key doesn't exists, and delete_api_key should return deleted status of False
    '''
    boto_conn.delete_api_key.side_effect = exceptions.ClientError(error_content, 'delete_api_key')
    result = boto_apigateway.delete_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2', **pytest.conn_parameters)

    assert not result.get('deleted')

def test_that_when_updating_an_api_key_description_successfully_the_update_api_key_description_method_returns_true(boto_conn):
    '''
    Test True if api key descriptipn update is successful
    '''
    boto_conn.update_api_key.return_value = api_key_ret
    result = boto_apigateway.update_api_key_description(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                                        description='test-lambda-api-key', **pytest.conn_parameters)
    assert result.get('updated')

def test_that_when_updating_an_api_key_description_for_a_key_that_does_not_exist_the_update_api_key_description_method_returns_false(boto_conn):
    '''
    Test False if api key doesn't exists for the update request
    '''
    boto_conn.update_api_key.side_effect = exceptions.ClientError(error_content, 'update_api_key')
    result = boto_apigateway.update_api_key_description(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                                        description='test-lambda-api-key', **pytest.conn_parameters)
    assert not result.get('updated')

def test_that_when_enabling_an_api_key_that_exists_the_enable_api_key_method_returns_api_key(boto_conn):
    '''
    Test True for the status of the enabled flag of the returned api key
    '''
    boto_conn.update_api_key.return_value = api_key_ret
    result = boto_apigateway.enable_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                            **pytest.conn_parameters)
    assert result.get('apiKey', {}).get('enabled')

def test_that_when_enabling_an_api_key_that_does_not_exist_the_enable_api_key_method_returns_error(boto_conn):
    '''
    Test Equality of the returned value of 'erorr'
    '''
    boto_conn.update_api_key.side_effect = exceptions.ClientError(error_content, 'update_api_key')
    result = boto_apigateway.enable_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                            **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('update_api_key')

def test_that_when_disabling_an_api_key_that_exists_the_disable_api_key_method_returns_api_key(boto_conn):
    '''
    Test False for the status of the enabled flag of the returned api key
    '''
    boto_conn.update_api_key.return_value = api_key_ret.copy()
    boto_conn.update_api_key.return_value['enabled'] = False
    result = boto_apigateway.disable_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                             **pytest.conn_parameters)
    assert not result.get('apiKey', {}).get('enabled')

def test_that_when_disabling_an_api_key_that_does_not_exist_the_disable_api_key_method_returns_error(boto_conn):
    '''
    Test Equality of the returned value of 'erorr'
    '''
    boto_conn.update_api_key.side_effect = exceptions.ClientError(error_content, 'update_api_key')
    result = boto_apigateway.disable_api_key(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                             **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('update_api_key')

def test_that_when_associating_stages_to_an_api_key_that_exists_the_associate_api_key_stagekeys_method_returns_true(boto_conn):
    '''
    Test True for returned value of 'associated'
    '''
    boto_conn.update_api_key.retuen_value = api_key_ret
    result = boto_apigateway.associate_api_key_stagekeys(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                                         stagekeyslist=[u'123yd1l123/test'],
                                                         **pytest.conn_parameters)
    assert result.get('associated')

def test_that_when_associating_stages_to_an_api_key_that_does_not_exist_the_associate_api_key_stagekeys_method_returns_false(boto_conn):
    '''
    Test False returned value of 'associated'
    '''
    boto_conn.update_api_key.side_effect = exceptions.ClientError(error_content, 'update_api_key')
    result = boto_apigateway.associate_api_key_stagekeys(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                                         stagekeyslist=[u'123yd1l123/test'],
                                                         **pytest.conn_parameters)
    assert not result.get('associated')

def test_that_when_disassociating_stages_to_an_api_key_that_exists_the_disassociate_api_key_stagekeys_method_returns_true(boto_conn):
    '''
    Test True for returned value of 'associated'
    '''
    boto_conn.update_api_key.retuen_value = None
    result = boto_apigateway.disassociate_api_key_stagekeys(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                                            stagekeyslist=[u'123yd1l123/test'],
                                                            **pytest.conn_parameters)
    assert result.get('disassociated')

def test_that_when_disassociating_stages_to_an_api_key_that_does_not_exist_the_disassociate_api_key_stagekeys_method_returns_false(boto_conn):
    '''
    Test False returned value of 'associated'
    '''
    boto_conn.update_api_key.side_effect = exceptions.ClientError(error_content, 'update_api_key')
    result = boto_apigateway.disassociate_api_key_stagekeys(apiKey='88883333amaa1ZMVGCoLeaTrQk8kzOC36vCgRcT2',
                                                            stagekeyslist=[u'123yd1l123/test'],
                                                            **pytest.conn_parameters)
    assert not result.get('disassociated')

def test_that_when_describing_api_deployments_the_describe_api_deployments_method_returns_list_of_deployments(boto_conn):
    '''
    Test Equality for number of deployments is 2
    '''
    boto_conn.get_deployments.return_value = {u'items': [{u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                                          u'id': u'n05smo'},
                                                         {u'createdDate': datetime.datetime(2015, 12, 2, 19, 51, 44),
                                                          u'id': u'n05sm1'}],
                                              'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.describe_api_deployments(restApiId='rm06h9oac4', **pytest.conn_parameters)
    assert len(result.get('deployments', {})) == 2

def test_that_when_describing_api_deployments_and_an_error_occurred_the_describe_api_deployments_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_deployments.side_effect = exceptions.ClientError(error_content, 'get_deployments')
    result = boto_apigateway.describe_api_deployments(restApiId='rm06h9oac4', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_deployments')

def test_that_when_describing_an_api_deployment_the_describe_api_deployment_method_returns_the_deployment(boto_conn):
    '''
    Test True for the returned deployment
    '''
    boto_conn.get_deployment.return_value = {u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                             u'id': u'n05smo',
                                             'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.describe_api_deployment(restApiId='rm06h9oac4', deploymentId='n05smo', **pytest.conn_parameters)
    assert result.get('deployment')

def test_that_when_describing_api_deployment_that_does_not_exist_the_describe_api_deployment_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_deployment.side_effect = exceptions.ClientError(error_content, 'get_deployment')
    result = boto_apigateway.describe_api_deployment(restApiId='rm06h9oac4', deploymentId='n05smo', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_deployment')

def test_that_when_activating_api_deployment_for_stage_and_deployment_that_exist_the_activate_api_deployment_method_returns_true(boto_conn):
    '''
    Test True for value of 'set'
    '''
    boto_conn.update_stage.return_value = {u'cacheClusterEnabled': False,
                                           u'cacheClusterStatus': 'NOT_AVAAILABLE',
                                           u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                           u'deploymentId': 'n05smo',
                                           u'description': 'test',
                                           u'lastUpdatedDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                           u'stageName': 'test',
                                           'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.activate_api_deployment(restApiId='rm06h9oac4', stageName='test', deploymentId='n05smo',
                                                     **pytest.conn_parameters)
    assert result.get('set')

def test_that_when_activating_api_deployment_for_stage_that_does_not_exist_the_activate_api_deployment_method_returns_false(boto_conn):
    '''
    Test False for value of 'set'
    '''
    boto_conn.update_stage.side_effect = exceptions.ClientError(error_content, 'update_stage')
    result = boto_apigateway.activate_api_deployment(restApiId='rm06h9oac4', stageName='test', deploymentId='n05smo',
                                                     **pytest.conn_parameters)
    assert not result.get('set')

def test_that_when_creating_an_api_deployment_succeeds_the_create_api_deployment_method_returns_true(boto_conn):
    '''
    tests that we can successfully create an api deployment and the createDate is
    converted to string
    '''
    now = datetime.datetime.now()
    boto_conn.create_deployment.return_value = {
        u'description': u'test-lambda-api-key',
        u'id': 'n05smo',
        u'createdDate': now,
        'ResponseMetadata': {'HTTPStatusCode': 200,
                             'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}

    result = boto_apigateway.create_api_deployment(restApiId='rm06h9oac4', stageName='test', **pytest.conn_parameters)
    deployment = result.get('deployment')
    now_str = '{0}'.format(now)

    assert result.get('created')
    assert deployment.get('createdDate') == now_str

def test_that_when_creating_an_deployment_fails_the_create_api_deployment_method_returns_error(boto_conn):
    '''
    tests that we properly handle errors when create an api deployment fails.
    '''

    boto_conn.create_deployment.side_effect = exceptions.ClientError(error_content, 'create_deployment')
    result = boto_apigateway.create_api_deployment(restApiId='rm06h9oac4', stageName='test', **pytest.conn_parameters)
    assert result.get('created') is False
    assert result.get('error').get('message') == error_message.format('create_deployment')

def test_that_when_deleting_an_api_deployment_that_exists_the_delete_api_deployment_method_returns_true(boto_conn):
    '''
    test True if the api deployment is successfully deleted.
    '''
    boto_conn.delete_deployment.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.delete_api_deployment(restApiId='rm06h9oac4', deploymentId='n05smo', **pytest.conn_parameters)
    assert result.get('deleted')

def test_that_when_deleting_an_api_deployment_that_does_not_exist_the_delete_api_deployment_method_returns_false(boto_conn):
    '''
    Test that the given api deployment doesn't exists, and delete_api_deployment should return deleted status of False
    '''
    boto_conn.delete_deployment.side_effect = exceptions.ClientError(error_content, 'delete_deployment')
    result = boto_apigateway.delete_api_deployment(restApiId='rm06h9oac4', deploymentId='n05smo1', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_describing_api_stages_the_describe_api_stages_method_returns_list_of_stages(boto_conn):
    '''
    Test Equality for number of stages for the given deployment is 2
    '''
    boto_conn.get_stages.return_value = {u'item': [{u'cacheClusterEnabled': False,
                                                    u'cacheClusterStatus': 'NOT_AVAILABLE',
                                                    u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                                    u'deploymentId': u'n05smo',
                                                    u'description': u'test',
                                                    u'lastUpdatedDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                                    u'stageName': u'test'},
                                                   {u'cacheClusterEnabled': False,
                                                    u'cacheClusterStatus': 'NOT_AVAILABLE',
                                                    u'createdDate': datetime.datetime(2015, 12, 17, 16, 33, 50),
                                                    u'deploymentId': u'n05smo',
                                                    u'description': u'dev',
                                                    u'lastUpdatedDate': datetime.datetime(2015, 12, 17, 16, 33, 50),
                                                    u'stageName': u'dev'}],
                                         'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.describe_api_stages(restApiId='rm06h9oac4', deploymentId='n05smo', **pytest.conn_parameters)
    assert len(result.get('stages', {})) == 2

def test_that_when_describing_api_stages_and_that_the_deployment_does_not_exist_the_describe_api_stages_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_stages.side_effect = exceptions.ClientError(error_content, 'get_stages')
    result = boto_apigateway.describe_api_stages(restApiId='rm06h9oac4', deploymentId='n05smo', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_stages')

def test_that_when_describing_an_api_stage_the_describe_api_stage_method_returns_the_stage(boto_conn):
    '''
    Test True for the returned stage
    '''
    boto_conn.get_stage.return_value = {u'cacheClusterEnabled': False,
                                        u'cacheClusterStatus': 'NOT_AVAILABLE',
                                        u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                        u'deploymentId': u'n05smo',
                                        u'description': u'test',
                                        u'lastUpdatedDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                        u'stageName': u'test',
                                        'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.describe_api_stage(restApiId='rm06h9oac4', stageName='test', **pytest.conn_parameters)
    assert result.get('stage')

def test_that_when_describing_api_stage_that_does_not_exist_the_describe_api_stage_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_stage.side_effect = exceptions.ClientError(error_content, 'get_stage')
    result = boto_apigateway.describe_api_stage(restApiId='rm06h9oac4', stageName='no_such_stage', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_stage')

def test_that_when_overwriting_stage_variables_to_an_existing_stage_the_overwrite_api_stage_variables_method_returns_the_updated_stage(boto_conn):
    '''
    Test True for the returned stage
    '''
    boto_conn.get_stage.return_value = {u'cacheClusterEnabled': False,
                                        u'cacheClusterStatus': 'NOT_AVAILABLE',
                                        u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                        u'deploymentId': u'n05smo',
                                        u'description': u'test',
                                        u'lastUpdatedDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                        u'stageName': u'test',
                                        u'variables': {'key1': 'val1'},
                                        'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    boto_conn.update_stage.return_value = {u'cacheClusterEnabled': False,
                                           u'cacheClusterStatus': 'NOT_AVAILABLE',
                                           u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                           u'deploymentId': u'n05smo',
                                           u'description': u'test',
                                           u'lastUpdatedDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                           u'stageName': u'test',
                                           u'variables': {'key1': 'val2'},
                                           'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.overwrite_api_stage_variables(restApiId='rm06h9oac4', stageName='test',
                                                           variables=dict(key1='val2'), **pytest.conn_parameters)
    assert result.get('stage').get('variables').get('key1') == 'val2'

def test_that_when_overwriting_stage_variables_to_a_nonexisting_stage_the_overwrite_api_stage_variables_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_stage.side_effect = exceptions.ClientError(error_content, 'get_stage')
    result = boto_apigateway.overwrite_api_stage_variables(restApiId='rm06h9oac4', stageName='no_such_stage',
                                                           variables=dict(key1="val1", key2="val2"), **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_stage')

def test_that_when_overwriting_stage_variables_to_an_existing_stage_the_overwrite_api_stage_variables_method_returns_error(boto_conn):
    '''
    Test Equality of error returned due to update_stage
    '''
    boto_conn.get_stage.return_value = {u'cacheClusterEnabled': False,
                                        u'cacheClusterStatus': 'NOT_AVAILABLE',
                                        u'createdDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                        u'deploymentId': u'n05smo',
                                        u'description': u'test',
                                        u'lastUpdatedDate': datetime.datetime(2015, 11, 17, 16, 33, 50),
                                        u'stageName': u'test',
                                        u'variables': {'key1': 'val1'},
                                        'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    boto_conn.update_stage.side_effect = exceptions.ClientError(error_content, 'update_stage')
    result = boto_apigateway.overwrite_api_stage_variables(restApiId='rm06h9oac4', stageName='test',
                                                           variables=dict(key1='val2'), **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('update_stage')

def test_that_when_creating_an_api_stage_succeeds_the_create_api_stage_method_returns_true(boto_conn):
    '''
    tests that we can successfully create an api stage and the createDate is
    converted to string
    '''
    now = datetime.datetime.now()
    boto_conn.create_stage.return_value = {u'cacheClusterEnabled': False,
                                           u'cacheClusterStatus': 'NOT_AVAILABLE',
                                           u'createdDate': now,
                                           u'deploymentId': u'n05smo',
                                           u'description': u'test',
                                           u'lastUpdatedDate': now,
                                           u'stageName': u'test',
                                           'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}

    result = boto_apigateway.create_api_stage(restApiId='rm06h9oac4', stageName='test', deploymentId='n05smo',
                                              **pytest.conn_parameters)
    stage = result.get('stage')
    now_str = '{0}'.format(now)
    assert result.get('created') is True
    assert stage.get('createdDate') == now_str
    assert stage.get('lastUpdatedDate') == now_str

def test_that_when_creating_an_api_stage_fails_the_create_api_stage_method_returns_error(boto_conn):
    '''
    tests that we properly handle errors when create an api stage fails.
    '''

    boto_conn.create_stage.side_effect = exceptions.ClientError(error_content, 'create_stage')
    result = boto_apigateway.create_api_stage(restApiId='rm06h9oac4', stageName='test', deploymentId='n05smo',
                                              **pytest.conn_parameters)
    assert result.get('created') is False
    assert result.get('error').get('message') == error_message.format('create_stage')

def test_that_when_deleting_an_api_stage_that_exists_the_delete_api_stage_method_returns_true(boto_conn):
    '''
    test True if the api stage is successfully deleted.
    '''
    boto_conn.delete_stage.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.delete_api_stage(restApiId='rm06h9oac4', stageName='test', **pytest.conn_parameters)
    assert result.get('deleted')

def test_that_when_deleting_an_api_stage_that_does_not_exist_the_delete_api_stage_method_returns_false(boto_conn):
    '''
    Test that the given api stage doesn't exists, and delete_api_stage should return deleted status of False
    '''
    boto_conn.delete_stage.side_effect = exceptions.ClientError(error_content, 'delete_stage')
    result = boto_apigateway.delete_api_stage(restApiId='rm06h9oac4', stageName='no_such_stage', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_flushing_api_stage_cache_for_an_existing_stage_the_flush_api_stage_cache_method_returns_true(boto_conn):
    '''
    Test True for 'flushed'
    '''
    boto_conn.flush_stage_cache.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.flush_api_stage_cache(restApiId='rm06h9oac4', stageName='no_such_stage', **pytest.conn_parameters)
    assert result.get('flushed')

def test_that_when_flushing_api_stage_cache_and_the_stage_does_not_exist_the_flush_api_stage_cache_method_returns_false(boto_conn):
    '''
    Test False for 'flushed'
    '''
    boto_conn.flush_stage_cache.side_effect = exceptions.ClientError(error_content, 'flush_stage_cache')
    result = boto_apigateway.flush_api_stage_cache(restApiId='rm06h9oac4', stageName='no_such_stage', **pytest.conn_parameters)
    assert not result.get('flushed')

def test_that_when_describing_api_models_the_describe_api_models_method_returns_list_of_models(boto_conn):
    '''
    Test Equality for number of models for the given api is 2
    '''
    boto_conn.get_models.return_value = {u'items': [{u'contentType': u'application/json',
                                                     u'name': u'Error',
                                                     u'description': u'Error Model',
                                                     u'id': u'iltqcb',
                                                     u'schema': u'{"properties":{"code":{"type":"integer","format":"int32"},"message":{"type":"string"},"fields":{"type":"string"}},"definitions":{}}'},
                                                    {u'contentType': u'application/json',
                                                     u'name': u'User',
                                                     u'description': u'User Model',
                                                     u'id': u'iltqcc',
                                                     u'schema': u'{"properties":{"username":{"type":"string","description":"A unique username for the user"},"password":{"type":"string","description":"A password for the new user"}},"definitions":{}}'}],
                                         'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.describe_api_models(restApiId='rm06h9oac4', **pytest.conn_parameters)
    assert len(result.get('models', {})) == 2

def test_that_when_describing_api_models_and_that_the_api_does_not_exist_the_describe_api_models_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_models.side_effect = exceptions.ClientError(error_content, 'get_models')
    result = boto_apigateway.describe_api_models(restApiId='rm06h9oac4', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_models')

def test_that_when_describing_api_model_the_describe_api_model_method_returns_the_model(boto_conn):
    '''
    Test True for the returned stage
    '''
    boto_conn.get_model.return_value = api_model_ret
    result = boto_apigateway.describe_api_model(restApiId='rm06h9oac4', modelName='Error', **pytest.conn_parameters)
    assert result.get('model')

def test_that_when_describing_api_model_and_that_the_model_does_not_exist_the_describe_api_model_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_model.side_effect = exceptions.ClientError(error_content, 'get_model')
    result = boto_apigateway.describe_api_model(restApiId='rm06h9oac4', modelName='Error', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_model')

def test_that_model_exists_the_api_model_exists_method_returns_true(boto_conn):
    '''
    Tests True when model exists
    '''
    boto_conn.get_model.return_value = api_model_ret
    result = boto_apigateway.api_model_exists(restApiId='rm06h9oac4', modelName='Error', **pytest.conn_parameters)
    assert result.get('exists')

def test_that_model_does_not_exists_the_api_model_exists_method_returns_false(boto_conn):
    '''
    Tests False when model does not exist
    '''
    boto_conn.get_model.side_effect = exceptions.ClientError(error_content, 'get_model')
    result = boto_apigateway.api_model_exists(restApiId='rm06h9oac4', modelName='Error', **pytest.conn_parameters)
    assert not result.get('exists')

def test_that_updating_model_schema_the_update_api_model_schema_method_returns_true(boto_conn):
    '''
    Tests True when model schema is updated.
    '''
    boto_conn.update_model.return_value = api_model_ret
    result = boto_apigateway.update_api_model_schema(restApiId='rm06h9oac4', modelName='Error',
                                                     schema=api_model_error_schema, **pytest.conn_parameters)
    assert result.get('updated')

def test_that_updating_model_schema_when_model_does_not_exist_the_update_api_model_schema_emthod_returns_false(boto_conn):
    '''
    Tests False when model schema is not upated.
    '''
    boto_conn.update_model.side_effect = exceptions.ClientError(error_content, 'update_model')
    result = boto_apigateway.update_api_model_schema(restApiId='rm06h9oac4', modelName='no_such_model',
                                                     schema=api_model_error_schema, **pytest.conn_parameters)
    assert not result.get('updated')

def test_that_when_creating_an_api_model_succeeds_the_create_api_model_method_returns_true(boto_conn):
    '''
    tests that we can successfully create an api model
    '''
    boto_conn.create_model.return_value = api_model_ret
    result = boto_apigateway.create_api_model(restApiId='rm06h9oac4', modelName='Error',
                                              modelDescription='Error Model', schema=api_model_error_schema,
                                              **pytest.conn_parameters)
    assert result.get('created')

def test_that_when_creating_an_api_model_fails_the_create_api_model_method_returns_error(boto_conn):
    '''
    tests that we properly handle errors when create an api model fails.
    '''
    boto_conn.create_model.side_effect = exceptions.ClientError(error_content, 'create_model')
    result = boto_apigateway.create_api_model(restApiId='rm06h9oac4', modelName='Error',
                                              modelDescription='Error Model', schema=api_model_error_schema,
                                              **pytest.conn_parameters)
    assert not result.get('created')

def test_that_when_deleting_an_api_model_that_exists_the_delete_api_model_method_returns_true(boto_conn):
    '''
    test True if the api model is successfully deleted.
    '''
    boto_conn.delete_model.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.delete_api_model(restApiId='rm06h9oac4', modelName='Error', **pytest.conn_parameters)
    assert result.get('deleted')

def test_that_when_deleting_an_api_model_that_does_not_exist_the_delete_api_model_method_returns_false(boto_conn):
    '''
    Test that the given api model doesn't exists, and delete_api_model should return deleted status of False
    '''
    boto_conn.delete_model.side_effect = exceptions.ClientError(error_content, 'delete_model')
    result = boto_apigateway.delete_api_model(restApiId='rm06h9oac4', modelName='no_such_model', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_describing_api_resources_the_describe_api_resources_method_returns_list_of_3_resources(boto_conn):
    '''
    Test Equality for number of resources for the given api is 3
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.describe_api_resources(restApiId='rm06h9oac4', **pytest.conn_parameters)
    assert len(result.get('resources')) == len(api_resources_ret.get('items'))

def test_that_when_describing_api_resources_and_that_the_api_does_not_exist_the_describe_api_resources_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_resources.side_effect = exceptions.ClientError(error_content, 'get_resources')
    result = boto_apigateway.describe_api_resources(restApiId='rm06h9oac4', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_resources')

def test_that_when_describing_an_api_resource_that_exists_the_describe_api_resource_method_returns_the_resource(boto_conn):
    '''
    Test Equality of the resource path returned is /api
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.describe_api_resource(restApiId='rm06h9oac4', path="/api", **pytest.conn_parameters)
    assert result.get('resource', {}).get('path') == '/api'

def test_that_when_describing_an_api_resource_that_does_not_exist_the_describe_api_resource_method_returns_the_resource_as_none(boto_conn):
    '''
    Test Equality of the 'resource' is None
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.describe_api_resource(restApiId='rm06h9oac4', path='/path/does/not/exist',
                                                   **pytest.conn_parameters)
    assert result.get('resource') == None

def test_that_when_describing_an_api_resource_and_that_the_api_does_not_exist_the_describe_api_resource_method_returns_error(boto_conn):
    '''
    Test Equality of error returned
    '''
    boto_conn.get_resources.side_effect = exceptions.ClientError(error_content, 'get_resources')
    result = boto_apigateway.describe_api_resource(restApiId='bad_id', path="/api", **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_resources')

def test_that_when_creating_api_resources_for_a_path_that_creates_one_new_resource_the_create_resources_api_method_returns_all_resources(boto_conn):
    '''
    Tests that a path of '/api3' returns 2 resources, named '/' and '/api'.
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.create_resource.return_value = api_create_resource_ret

    result = boto_apigateway.create_api_resources(restApiId='rm06h9oac4', path='/api3', **pytest.conn_parameters)

    resources = result.get('resources')
    assert result.get('created') is True
    assert len(resources) == 2
    assert resources[0].get('path') == '/'
    assert resources[1].get('path') == '/api3'

def test_that_when_creating_api_resources_for_a_path_whose_resources_exist_the_create_resources_api_method_returns_all_resources(boto_conn):
    '''
    Tests that a path of '/api/users' as defined in api_resources_ret return resources named '/', '/api',
    and '/api/users'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.create_api_resources(restApiId='rm06h9oac4', path='/api/users', **pytest.conn_parameters)
    resources = result.get('resources')
    assert result.get('created') is True
    assert len(resources) == len(api_resources_ret.get('items'))
    assert resources[0].get('path') == '/'
    assert resources[1].get('path') == '/api'
    assert resources[2].get('path') == '/api/users'

def test_that_when_creating_api_resource_fails_the_create_resources_api_method_returns_false(boto_conn):
    '''
    Tests False if we failed to create a resource
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.create_resource.side_effect = exceptions.ClientError(error_content, 'create_resource')
    result = boto_apigateway.create_api_resources(restApiId='rm06h9oac4', path='/api4', **pytest.conn_parameters)
    assert not result.get('created')

def test_that_when_deleting_api_resources_for_a_resource_that_exists_the_delete_api_resources_method_returns_true(boto_conn):
    '''
    Tests True for '/api'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.delete_api_resources(restApiId='rm06h9oac4', path='/api', **pytest.conn_parameters)
    assert result.get('deleted')

def test_that_when_deleting_api_resources_for_a_resource_that_does_not_exist_the_delete_api_resources_method_returns_false(boto_conn):
    '''
    Tests False for '/api5'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.delete_api_resources(restApiId='rm06h9oac4', path='/api5', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_deleting_the_root_api_resource_the_delete_api_resources_method_returns_false(boto_conn):
    '''
    Tests False for '/'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.delete_api_resources(restApiId='rm06h9oac4', path='/', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_deleting_api_resources_and_delete_resource_throws_error_the_delete_api_resources_method_returns_false(boto_conn):
    '''
    Tests False delete_resource side side_effect
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.delete_resource.side_effect = exceptions.ClientError(error_content, 'delete_resource')
    result = boto_apigateway.delete_api_resources(restApiId='rm06h9oac4', path='/api', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_describing_an_api_resource_method_that_exists_the_describe_api_resource_method_returns_the_method(boto_conn):
    '''
    Tests True for '/api/users' and POST
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_method.return_value = {u'httpMethod': 'POST',
                                         'ResponseMetadata': {'HTTPStatusCode': 200,
                                                              'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}
    result = boto_apigateway.describe_api_resource_method(restApiId='rm06h9oac4',
                                                          resourcePath='/api/users',
                                                          httpMethod='POST', **pytest.conn_parameters)
    assert result.get('method')

def test_that_when_describing_an_api_resource_method_whose_method_does_not_exist_the_describe_api_resource_method_returns_error(boto_conn):
    '''
    Tests Equality of returned error for '/api/users' and PUT
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_method.side_effect = exceptions.ClientError(error_content, 'get_method')
    result = boto_apigateway.describe_api_resource_method(restApiId='rm06h9oac4',
                                                          resourcePath='/api/users',
                                                          httpMethod='PUT', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_method')

def test_that_when_describing_an_api_resource_method_whose_resource_does_not_exist_the_describe_api_resrouce_method_returns_error(boto_conn):
    '''
    Tests True for resource not found error for '/does/not/exist' and POST
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.describe_api_resource_method(restApiId='rm06h9oac4',
                                                          resourcePath='/does/not/exist',
                                                          httpMethod='POST', **pytest.conn_parameters)
    assert result.get('error')

def test_that_when_creating_an_api_method_the_create_api_method_method_returns_true(boto_conn):
    '''
    Tests True on 'created' for '/api/users' and 'GET'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.put_method.return_value = {u'httpMethod': 'GET',
                                         'ResponseMetadata': {'HTTPStatusCode': 200,
                                                              'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}
    result = boto_apigateway.create_api_method(restApiId='rm06h9oac4',
                                               resourcePath='/api/users',
                                               httpMethod='GET',
                                               authorizationType='NONE', **pytest.conn_parameters)
    assert result.get('created')

def test_that_when_creating_an_api_method_and_resource_does_not_exist_the_create_api_method_method_returns_false(boto_conn):
    '''
    Tests False on 'created' for '/api5', and 'GET'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.create_api_method(restApiId='rm06h9oac4',
                                               resourcePath='/api5',
                                               httpMethod='GET',
                                               authorizationType='NONE', **pytest.conn_parameters)
    assert not result.get('created')

def test_that_when_creating_an_api_method_and_error_thrown_on_put_method_the_create_api_method_method_returns_false(boto_conn):
    '''
    Tests False on 'created' for '/api/users' and 'GET'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.put_method.side_effect = exceptions.ClientError(error_content, 'put_method')
    result = boto_apigateway.create_api_method(restApiId='rm06h9oac4',
                                               resourcePath='/api/users',
                                               httpMethod='GET',
                                               authorizationType='NONE', **pytest.conn_parameters)
    assert not result.get('created')

def test_that_when_deleting_an_api_method_for_a_method_that_exist_the_delete_api_method_method_returns_true(boto_conn):
    '''
    Tests True for '/api/users' and 'POST'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.delete_method.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.delete_api_method(restApiId='rm06h9oac4', resourcePath='/api/users',
                                               httpMethod='POST', **pytest.conn_parameters)
    assert result.get('deleted')

def test_that_when_deleting_an_api_method_for_a_method_that_does_not_exist_the_delete_api_method_method_returns_false(boto_conn):
    '''
    Tests False for '/api/users' and 'GET'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.delete_method.side_effect = exceptions.ClientError(error_content, 'delete_method')
    result = boto_apigateway.delete_api_method(restApiId='rm06h9oac4', resourcePath='/api/users',
                                               httpMethod='GET', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_deleting_an_api_method_for_a_resource_that_does_not_exist_the_delete_api_method_method_returns_false(boto_conn):
    '''
    Tests False for '/api/users5' and 'POST'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.delete_api_method(restApiId='rm06h9oac4', resourcePath='/api/users5',
                                               httpMethod='POST', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_describing_an_api_method_response_that_exists_the_describe_api_method_respond_method_returns_the_response(boto_conn):
    '''
    Tests True for 'response' for '/api/users', 'POST', and 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_method_response.return_value = {u'statusCode': 200,
                                                  'ResponseMetadata': {'HTTPStatusCode': 200,
                                                                       'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}
    result = boto_apigateway.describe_api_method_response(restApiId='rm06h9oac4',
                                                          resourcePath='/api/users',
                                                          httpMethod='POST',
                                                          statusCode=200, **pytest.conn_parameters)
    assert result.get('response')

def test_that_when_describing_an_api_method_response_and_response_code_does_not_exist_the_describe_api_method_response_method_returns_error(boto_conn):
    '''
    Tests Equality of error msg thrown from get_method_response for '/api/users', 'POST', and 250
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_method_response.side_effect = exceptions.ClientError(error_content, 'get_method_response')
    result = boto_apigateway.describe_api_method_response(restApiId='rm06h9oac4',
                                                          resourcePath='/api/users',
                                                          httpMethod='POST',
                                                          statusCode=250, **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_method_response')

def test_that_when_describing_an_api_method_response_and_resource_does_not_exist_the_describe_api_method_response_method_returns_error(boto_conn):
    '''
    Tests True for existence of 'error' for '/api5/users', 'POST', and 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.describe_api_method_response(restApiId='rm06h9oac4',
                                                          resourcePath='/api5/users',
                                                          httpMethod='POST',
                                                          statusCode=200, **pytest.conn_parameters)
    assert result.get('error')

def test_that_when_creating_an_api_method_response_the_create_api_method_response_method_returns_true(boto_conn):
    '''
    Tests True on 'created' for '/api/users', 'POST', 201
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.put_method_response.return_value = {u'statusCode': '201',
                                                  'ResponseMetadata': {'HTTPStatusCode': 200,
                                                                       'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}
    result = boto_apigateway.create_api_method_response(restApiId='rm06h9oac4',
                                                        resourcePath='/api/users',
                                                        httpMethod='POST',
                                                        statusCode='201', **pytest.conn_parameters)
    assert result.get('created')

def test_that_when_creating_an_api_method_response_and_resource_does_not_exist_the_create_api_method_response_method_returns_false(boto_conn):
    '''
    Tests False on 'created' for '/api5', 'POST', 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.create_api_method_response(restApiId='rm06h9oac4',
                                                        resourcePath='/api5',
                                                        httpMethod='POST',
                                                        statusCode='200', **pytest.conn_parameters)
    assert not result.get('created')

def test_that_when_creating_an_api_method_response_and_error_thrown_on_put_method_response_the_create_api_method_response_method_returns_false(boto_conn):
    '''
    Tests False on 'created' for '/api/users', 'POST', 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.put_method_response.side_effect = exceptions.ClientError(error_content, 'put_method_response')
    result = boto_apigateway.create_api_method_response(restApiId='rm06h9oac4',
                                                        resourcePath='/api/users',
                                                        httpMethod='POST',
                                                        statusCode='200', **pytest.conn_parameters)
    assert not result.get('created')

def test_that_when_deleting_an_api_method_response_for_a_response_that_exist_the_delete_api_method_response_method_returns_true(boto_conn):
    '''
    Tests True for '/api/users', 'POST', 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.delete_method_response.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '2d31072c-9d15-11e5-9977-6d9fcfda9c0a'}}
    result = boto_apigateway.delete_api_method_response(restApiId='rm06h9oac4', resourcePath='/api/users',
                                                        httpMethod='POST', statusCode='200', **pytest.conn_parameters)
    assert result.get('deleted')

def test_that_when_deleting_an_api_method_response_for_a_response_that_does_not_exist_the_delete_api_method_response_method_returns_false(boto_conn):
    '''
    Tests False for '/api/users', 'POST', 201
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.delete_method_response.side_effect = exceptions.ClientError(error_content, 'delete_method_response')
    result = boto_apigateway.delete_api_method_response(restApiId='rm06h9oac4', resourcePath='/api/users',
                                                        httpMethod='GET', statusCode='201', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_deleting_an_api_method_response_for_a_resource_that_does_not_exist_the_delete_api_method_response_method_returns_false(boto_conn):
    '''
    Tests False for '/api/users5', 'POST', 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.delete_api_method_response(restApiId='rm06h9oac4', resourcePath='/api/users5',
                                                        httpMethod='POST', statusCode='200', **pytest.conn_parameters)
    assert not result.get('deleted')

def test_that_when_describing_an_api_integration_that_exists_the_describe_api_integration_method_returns_the_intgration(boto_conn):
    '''
    Tests True for 'integration' for '/api/users', 'POST'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_integration.return_value = {u'type': 'AWS',
                                              u'uri': 'arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:1234568992820:function:echo_event/invocations',
                                              u'credentials': 'testing',
                                              u'httpMethod': 'POST',
                                              u'intgrationResponses': {'200': {}},
                                              u'requestTemplates': {'application/json': {}},
                                              'ResponseMetadata': {'HTTPStatusCode': 200,
                                                                   'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}
    result = boto_apigateway.describe_api_integration(restApiId='rm06h9oac4',
                                                      resourcePath='/api/users',
                                                      httpMethod='POST',
                                                      **pytest.conn_parameters)
    assert result.get('integration')

def test_that_when_describing_an_api_integration_and_method_does_not_have_integration_defined_the_describe_api_integration_method_returns_error(boto_conn):
    '''
    Tests Equality of error msg thrown from get_method_response for '/api/users', 'GET'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_integration.side_effect = exceptions.ClientError(error_content, 'get_integration')
    result = boto_apigateway.describe_api_integration(restApiId='rm06h9oac4',
                                                      resourcePath='/api/users',
                                                      httpMethod='GET',
                                                      **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_integration')

def test_that_when_describing_an_api_integration_and_resource_does_not_exist_the_describe_api_integration_method_returns_error(boto_conn):
    '''
    Tests True for existence of 'error' for '/api5/users', 'POST'
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.describe_api_integration(restApiId='rm06h9oac4',
                                                      resourcePath='/api5/users',
                                                      httpMethod='POST',
                                                      **pytest.conn_parameters)
    assert result.get('error')

def test_that_when_describing_an_api_integration_response_that_exists_the_describe_api_integration_response_method_returns_the_intgration(boto_conn):
    '''
    Tests True for 'response' for '/api/users', 'POST', 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_integration_response.return_value = {u'responseParameters': {},
                                                       u'statusCode': 200,
                                                       'ResponseMetadata': {'HTTPStatusCode': 200,
                                                                            'RequestId': '7cc233dd-9dc8-11e5-ba47-1b7350cc2757'}}
    result = boto_apigateway.describe_api_integration_response(restApiId='rm06h9oac4',
                                                               resourcePath='/api/users',
                                                               httpMethod='POST',
                                                               statusCode='200',
                                                               **pytest.conn_parameters)
    assert result.get('response')

def test_that_when_describing_an_api_integration_response_and_status_code_does_not_exist_the_describe_api_integration_response_method_returns_error(boto_conn):
    '''
    Tests Equality of error msg thrown from get_method_response for '/api/users', 'POST', 201
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    boto_conn.get_integration_response.side_effect = exceptions.ClientError(error_content, 'get_integration_response')
    result = boto_apigateway.describe_api_integration_response(restApiId='rm06h9oac4',
                                                               resourcePath='/api/users',
                                                               httpMethod='POST',
                                                               statusCode='201',
                                                               **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_integration_response')

def test_that_when_describing_an_api_integration_response_and_resource_does_not_exist_the_describe_api_integration_response_method_returns_error(boto_conn):
    '''
    Tests True for existence of 'error' for '/api5/users', 'POST', 200
    '''
    boto_conn.get_resources.return_value = api_resources_ret
    result = boto_apigateway.describe_api_integration_response(restApiId='rm06h9oac4',
                                                               resourcePath='/api5/users',
                                                               httpMethod='POST',
                                                               statusCode='200',
                                                               **pytest.conn_parameters)
    assert result.get('error')

def test_that_when_describing_usage_plans_and_an_exception_is_thrown_in_get_usage_plans(boto_conn):
    '''
    Tests True for existence of 'error'
    '''
    boto_conn.get_usage_plans.side_effect = exceptions.ClientError(error_content, 'get_usage_plans_exception')
    result = boto_apigateway.describe_usage_plans(name='some plan', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('get_usage_plans_exception')

def test_that_when_describing_usage_plans_and_plan_name_or_id_does_not_exist_that_results_have_empty_plans_list(boto_conn):
    '''
    Tests for plans equaling empty list
    '''
    boto_conn.get_usage_plans.return_value = usage_plans_ret

    result = boto_apigateway.describe_usage_plans(name='does not exist', **pytest.conn_parameters)
    assert result.get('plans') == []

    result = boto_apigateway.describe_usage_plans(plan_id='does not exist', **pytest.conn_parameters)
    assert result.get('plans') == []

    result = boto_apigateway.describe_usage_plans(name='does not exist', plan_id='does not exist', **pytest.conn_parameters)
    assert result.get('plans') == []

    result = boto_apigateway.describe_usage_plans(name='plan1_name', plan_id='does not exist', **pytest.conn_parameters)
    assert result.get('plans') == []

    result = boto_apigateway.describe_usage_plans(name='does not exist', plan_id='plan1_id', **pytest.conn_parameters)
    assert result.get('plans') == []

def test_that_when_describing_usage_plans_for_plans_that_exist_that_the_function_returns_all_matching_plans(boto_conn):
    '''
    Tests for plans filtering properly if they exist
    '''
    boto_conn.get_usage_plans.return_value = usage_plans_ret

    result = boto_apigateway.describe_usage_plans(name=usage_plan1['name'], **pytest.conn_parameters)
    assert len(result.get('plans')) == 2
    for plan in result['plans']:
        assert plan in [usage_plan1, usage_plan1b]

def test_that_when_creating_or_updating_a_usage_plan_and_throttle_or_quota_failed_to_validate_that_an_error_is_returned(boto_conn):
    '''
    Tests for TypeError and ValueError in throttle and quota
    '''
    for throttle, quota in (([], None), (None, []), ('abc', None), (None, 'def')):
        res = boto_apigateway.create_usage_plan('plan1_name', description=None, throttle=throttle, quota=quota, **pytest.conn_parameters)
        assert None != res.get('error')
        res = boto_apigateway.update_usage_plan('plan1_id', throttle=throttle, quota=quota, **pytest.conn_parameters)
        assert None != res.get('error')

    for quota in ({'limit': 123}, {'period': 123}, {'period': 'DAY'}):
        res = boto_apigateway.create_usage_plan('plan1_name', description=None, throttle=None, quota=quota, **pytest.conn_parameters)
        assert None != res.get('error')
        res = boto_apigateway.update_usage_plan('plan1_id', quota=quota, **pytest.conn_parameters)
        assert None != res.get('error')

    assert boto_conn.conn.get_usage_plans.call_count == 0
    assert boto_conn.conn.create_usage_plan.call_count == 0
    assert boto_conn.conn.update_usage_plan.call_count == 0

def test_that_when_creating_a_usage_plan_and_create_usage_plan_throws_an_exception_that_an_error_is_returned(boto_conn):
    '''
    tests for exceptions.ClientError
    '''
    boto_conn.create_usage_plan.side_effect = exceptions.ClientError(error_content, 'create_usage_plan_exception')
    result = boto_apigateway.create_usage_plan(name='some plan', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('create_usage_plan_exception')

def test_that_create_usage_plan_succeeds(boto_conn):
    '''
    tests for success user plan creation
    '''
    res = 'unit test create_usage_plan succeeded'
    boto_conn.create_usage_plan.return_value = res
    result = boto_apigateway.create_usage_plan(name='some plan', **pytest.conn_parameters)
    assert result.get('created') == True
    assert result.get('result') == res

def test_that_when_udpating_a_usage_plan_and_update_usage_plan_throws_an_exception_that_an_error_is_returned(boto_conn):
    '''
    tests for exceptions.ClientError
    '''
    boto_conn.update_usage_plan.side_effect = exceptions.ClientError(error_content, 'update_usage_plan_exception')
    result = boto_apigateway.update_usage_plan(plan_id='plan1_id', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format('update_usage_plan_exception')

def test_that_when_updating_a_usage_plan_and_if_throttle_and_quota_parameters_are_none_update_usage_plan_removes_throttle_and_quota(boto_conn):
    '''
    tests for throttle and quota removal
    '''
    ret = 'some success status'
    boto_conn.update_usage_plan.return_value = ret
    result = boto_apigateway.update_usage_plan(plan_id='plan1_id', throttle=None, quota=None, **pytest.conn_parameters)
    assert result.get('updated') == True
    assert result.get('result') == ret
    assert boto_conn.update_usage_plan.call_count >= 1

def test_that_when_deleting_usage_plan_and_describe_usage_plans_had_error_that_the_same_error_is_returned(boto_conn):
    '''
    tests for error in describe_usage_plans returns error
    '''
    ret = 'get_usage_plans_exception'
    boto_conn.get_usage_plans.side_effect = exceptions.ClientError(error_content, ret)
    result = boto_apigateway.delete_usage_plan(plan_id='some plan id', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format(ret)
    assert boto_conn.conn.delete_usage_plan.call_count == 0

def test_that_when_deleting_usage_plan_and_plan_exists_that_the_functions_returns_deleted_true(boto_conn):
    boto_conn.get_usage_plans.return_value = usage_plans_ret
    ret = 'delete_usage_plan_retval'
    boto_conn.delete_usage_plan.return_value = ret
    result = boto_apigateway.delete_usage_plan(plan_id='plan1_id', **pytest.conn_parameters)
    assert result.get('deleted') == True
    assert result.get('usagePlanId') == 'plan1_id'
    assert boto_conn.delete_usage_plan.call_count >= 1

def test_that_when_deleting_usage_plan_and_plan_does_not_exist_that_the_functions_returns_deleted_true(boto_conn):
    '''
    tests for exceptions.ClientError
    '''
    boto_conn.get_usage_plans.return_value = dict(
        items=[]
    )
    ret = 'delete_usage_plan_retval'
    boto_conn.delete_usage_plan.return_value = ret
    result = boto_apigateway.delete_usage_plan(plan_id='plan1_id', **pytest.conn_parameters)
    assert result.get('deleted') == True
    assert result.get('usagePlanId') == 'plan1_id'
    assert boto_conn.conn.delete_usage_plan.call_count == 0

def test_that_when_deleting_usage_plan_and_delete_usage_plan_throws_exception_that_an_error_is_returned(boto_conn):
    '''
    tests for exceptions.ClientError
    '''
    boto_conn.get_usage_plans.return_value = usage_plans_ret
    error_msg = 'delete_usage_plan_exception'
    boto_conn.delete_usage_plan.side_effect = exceptions.ClientError(error_content, error_msg)
    result = boto_apigateway.delete_usage_plan(plan_id='plan1_id', **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format(error_msg)
    assert boto_conn.delete_usage_plan.call_count >= 1

def test_that_attach_or_detach_usage_plan_when_apis_is_empty_that_success_is_returned(boto_conn):
    '''
    tests for border cases when apis is empty list
    '''
    result = boto_apigateway.attach_usage_plan_to_apis(plan_id='plan1_id', apis=[], **pytest.conn_parameters)
    assert result.get('success') == True
    assert result.get('result', 'no result?') == None
    assert boto_conn.conn.update_usage_plan.call_count == 0

    result = boto_apigateway.detach_usage_plan_from_apis(plan_id='plan1_id', apis=[], **pytest.conn_parameters)
    assert result.get('success') == True
    assert result.get('result', 'no result?') == None
    assert boto_conn.conn.update_usage_plan.call_count == 0

def test_that_attach_or_detach_usage_plan_when_api_does_not_contain_apiId_or_stage_that_an_error_is_returned(boto_conn):
    '''
    tests for invalid key in api object
    '''
    for api in ({'apiId': 'some Id'}, {'stage': 'some stage'}, {}):
        result = boto_apigateway.attach_usage_plan_to_apis(plan_id='plan1_id', apis=[api], **pytest.conn_parameters)
        assert result.get('error') != None

        result = boto_apigateway.detach_usage_plan_from_apis(plan_id='plan1_id', apis=[api], **pytest.conn_parameters)
        assert result.get('error') != None

    assert boto_conn.conn.update_usage_plan.call_count == 0

def test_that_attach_or_detach_usage_plan_and_update_usage_plan_throws_exception_that_an_error_is_returned(boto_conn):
    '''
    tests for exceptions.ClientError
    '''
    api = {'apiId': 'some_id', 'stage': 'some_stage'}
    error_msg = 'update_usage_plan_exception'
    boto_conn.update_usage_plan.side_effect = exceptions.ClientError(error_content, error_msg)

    result = boto_apigateway.attach_usage_plan_to_apis(plan_id='plan1_id', apis=[api], **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format(error_msg)

    result = boto_apigateway.detach_usage_plan_from_apis(plan_id='plan1_id', apis=[api], **pytest.conn_parameters)
    assert result.get('error').get('message') == error_message.format(error_msg)

def test_that_attach_or_detach_usage_plan_updated_successfully(boto_conn):
    '''
    tests for update_usage_plan called
    '''
    api = {'apiId': 'some_id', 'stage': 'some_stage'}
    attach_ret = 'update_usage_plan_add_op_succeeded'
    detach_ret = 'update_usage_plan_remove_op_succeeded'
    boto_conn.update_usage_plan.side_effect = [attach_ret, detach_ret]

    result = boto_apigateway.attach_usage_plan_to_apis(plan_id='plan1_id', apis=[api], **pytest.conn_parameters)
    assert result.get('success') == True
    assert result.get('result') == attach_ret

    result = boto_apigateway.detach_usage_plan_from_apis(plan_id='plan1_id', apis=[api], **pytest.conn_parameters)
    assert result.get('success') == True
    assert result.get('result') == detach_ret
