# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals

# Import Fractus Libs
import fractus.cloudutils.botomod as botomod
import fractus.cloudstates.boto_vpc as boto_vpc

# Import Test Libs
import pytest
from mock import patch
pytestmark = pytest.mark.skip('all tests still WIP')

boto = pytest.importorskip('boto', minversion='2.8.0')
boto3 = pytest.importorskip('boto3')
moto = pytest.importorskip('moto')
exception = pytest.importorskip('boto.exception')

cidr_block = '10.0.0.0/24'
subnet_id = 'subnet-123456'
dhcp_options_parameters = {'domain_name': 'example.com', 'domain_name_servers': ['1.2.3.4'], 'ntp_servers': ['5.6.7.8'],
                           'netbios_name_servers': ['10.0.0.1'], 'netbios_node_type': 2}
network_acl_entry_parameters = ('fake', 100, -1, 'allow', cidr_block)
dhcp_options_parameters.update(pytest.conn_parameters)


def setup_module():
    serializers = salt.loader.serializers(self.opts)
    return {
        boto_vpc: {
            '__opts__': pytest.opts,
            '__salt__': pytest.modules,
            '__utils__': pytest.utils,
            '__states__': pytest.states,
            '__serializers__': serializers,
        },
        botomod: {}
    }

class TestBotoVpc(object):
    '''
    TestCase for salt.states.boto_vpc state.module
    '''

    @moto.mock_ec2_deprecated
    def test_present_when_vpc_does_not_exist(self):
        '''
        Tests present on a VPC that does not exist.
        '''
        with patch.dict(botomod.__salt__, self.funcs):
            vpc_present_result = self.salt_states['boto_vpc.present']('test', cidr_block)

        self.assertTrue(vpc_present_result['result'])
        self.assertEqual(vpc_present_result['changes']['new']['vpc']['state'], 'available')

    @moto.mock_ec2_deprecated
    def test_present_when_vpc_exists(self):
        vpc = self._create_vpc(name='test')
        vpc_present_result = self.salt_states['boto_vpc.present']('test', cidr_block)
        self.assertTrue(vpc_present_result['result'])
        self.assertEqual(vpc_present_result['changes'], {})

    @moto.mock_ec2_deprecated
    @pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
    def test_present_with_failure(self):
        with patch('moto.ec2.models.VPCBackend.create_vpc', side_effect=exception.BotoServerError(400, 'Mocked error')):
            vpc_present_result = self.salt_states['boto_vpc.present']('test', cidr_block)
            self.assertFalse(vpc_present_result['result'])
            self.assertTrue('Mocked error' in vpc_present_result['comment'])

    @moto.mock_ec2_deprecated
    def test_absent_when_vpc_does_not_exist(self):
        '''
        Tests absent on a VPC that does not exist.
        '''
        with patch.dict(botomod.__salt__, self.funcs):
            vpc_absent_result = self.salt_states['boto_vpc.absent']('test')
        self.assertTrue(vpc_absent_result['result'])
        self.assertEqual(vpc_absent_result['changes'], {})

    @moto.mock_ec2_deprecated
    def test_absent_when_vpc_exists(self):
        vpc = self._create_vpc(name='test')
        with patch.dict(botomod.__salt__, self.funcs):
            vpc_absent_result = self.salt_states['boto_vpc.absent']('test')
        self.assertTrue(vpc_absent_result['result'])
        self.assertEqual(vpc_absent_result['changes']['new']['vpc'], None)

    @moto.mock_ec2_deprecated
    @pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
    def test_absent_with_failure(self):
        vpc = self._create_vpc(name='test')
        with patch('moto.ec2.models.VPCBackend.delete_vpc', side_effect=exception.BotoServerError(400, 'Mocked error')):
            vpc_absent_result = self.salt_states['boto_vpc.absent']('test')
            self.assertFalse(vpc_absent_result['result'])
            self.assertTrue('Mocked error' in vpc_absent_result['comment'])


class BotoVpcResourceMixin(object):
    resource_type = None
    backend_create = None
    backend_delete = None
    extra_kwargs = {}

    def _create_resource(self, vpc_id=None, name=None):
        _create = getattr(self, '_create_' + self.resource_type)
        _create(vpc_id=vpc_id, name=name, **self.extra_kwargs)

    @moto.mock_ec2_deprecated
    def test_present_when_resource_does_not_exist(self):
        '''
        Tests present on a resource that does not exist.
        '''
        vpc = self._create_vpc(name='test')
        with patch.dict(botomod.__salt__, self.funcs):
            resource_present_result = self.salt_states['boto_vpc.{0}_present'.format(self.resource_type)](
                name='test', vpc_name='test', **self.extra_kwargs)

        self.assertTrue(resource_present_result['result'])

        exists = self.funcs['boto_vpc.resource_exists'](self.resource_type, 'test').get('exists')
        self.assertTrue(exists)

    @moto.mock_ec2_deprecated
    def test_present_when_resource_exists(self):
        vpc = self._create_vpc(name='test')
        resource = self._create_resource(vpc_id=vpc.id, name='test')
        with patch.dict(botomod.__salt__, self.funcs):
            resource_present_result = self.salt_states['boto_vpc.{0}_present'.format(self.resource_type)](
                    name='test', vpc_name='test', **self.extra_kwargs)
        self.assertTrue(resource_present_result['result'])
        self.assertEqual(resource_present_result['changes'], {})

    @moto.mock_ec2_deprecated
    @pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
    def test_present_with_failure(self):
        vpc = self._create_vpc(name='test')
        with patch('moto.ec2.models.{0}'.format(self.backend_create), side_effect=exception.BotoServerError(400, 'Mocked error')):
            resource_present_result = self.salt_states['boto_vpc.{0}_present'.format(self.resource_type)](
                    name='test', vpc_name='test', **self.extra_kwargs)

            self.assertFalse(resource_present_result['result'])
            self.assertTrue('Mocked error' in resource_present_result['comment'])

    @moto.mock_ec2_deprecated
    def test_absent_when_resource_does_not_exist(self):
        '''
        Tests absent on a resource that does not exist.
        '''
        with patch.dict(botomod.__salt__, self.funcs):
            resource_absent_result = self.salt_states['boto_vpc.{0}_absent'.format(self.resource_type)]('test')
        self.assertTrue(resource_absent_result['result'])
        self.assertEqual(resource_absent_result['changes'], {})

    @moto.mock_ec2_deprecated
    def test_absent_when_resource_exists(self):
        vpc = self._create_vpc(name='test')
        self._create_resource(vpc_id=vpc.id, name='test')

        with patch.dict(botomod.__salt__, self.funcs):
            resource_absent_result = self.salt_states['boto_vpc.{0}_absent'.format(self.resource_type)]('test')
        self.assertTrue(resource_absent_result['result'])
        self.assertEqual(resource_absent_result['changes']['new'][self.resource_type], None)
        exists = self.funcs['boto_vpc.resource_exists'](self.resource_type, 'test').get('exists')
        self.assertFalse(exists)

    @moto.mock_ec2_deprecated
    @pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
    def test_absent_with_failure(self):
        vpc = self._create_vpc(name='test')
        self._create_resource(vpc_id=vpc.id, name='test')

        with patch('moto.ec2.models.{0}'.format(self.backend_delete), side_effect=exception.BotoServerError(400, 'Mocked error')):
            resource_absent_result = self.salt_states['boto_vpc.{0}_absent'.format(self.resource_type)]('test')
            self.assertFalse(resource_absent_result['result'])
            self.assertTrue('Mocked error' in resource_absent_result['comment'])


class TestBotoVpcSubnets(object):
    resource_type = 'subnet'
    backend_create = 'SubnetBackend.create_subnet'
    backend_delete = 'SubnetBackend.delete_subnet'
    extra_kwargs = {'cidr_block': cidr_block}


class TestBotoVpcInternetGateway(object):
    resource_type = 'internet_gateway'
    backend_create = 'InternetGatewayBackend.create_internet_gateway'
    backend_delete = 'InternetGatewayBackend.delete_internet_gateway'


class TestBotoVpcRouteTable(object):
    resource_type = 'route_table'
    backend_create = 'RouteTableBackend.create_route_table'
    backend_delete = 'RouteTableBackend.delete_route_table'

    @moto.mock_ec2_deprecated
    def test_present_with_subnets(self):
        vpc = self._create_vpc(name='test')
        subnet1 = self._create_subnet(vpc_id=vpc.id, name='test1')
        subnet2 = self._create_subnet(vpc_id=vpc.id, name='test2')

        route_table_present_result = self.salt_states['boto_vpc.route_table_present'](
                name='test', vpc_name='test', subnet_names=['test1'], subnet_ids=[subnet2.id])

        associations = route_table_present_result['changes']['new']['subnets_associations']

        assoc_subnets = [x['subnet_id'] for x in associations]
        self.assertEqual(set(assoc_subnets), set([subnet1.id, subnet2.id]))

        route_table_present_result = self.salt_states['boto_vpc.route_table_present'](
                name='test', vpc_name='test', subnet_ids=[subnet2.id])

        changes = route_table_present_result['changes']

        old_subnets = [x['subnet_id'] for x in changes['old']['subnets_associations']]
        self.assertEqual(set(assoc_subnets), set(old_subnets))

        new_subnets = changes['new']['subnets_associations']
        self.assertEqual(new_subnets[0]['subnet_id'], subnet2.id)

    @moto.mock_ec2_deprecated
    def test_present_with_routes(self):
        vpc = self._create_vpc(name='test')
        igw = self._create_internet_gateway(name='test', vpc_id=vpc.id)

        with patch.dict(botomod.__salt__, self.funcs):
            route_table_present_result = self.salt_states['boto_vpc.route_table_present'](
                    name='test', vpc_name='test', routes=[{'destination_cidr_block': '0.0.0.0/0',
                                                           'gateway_id': igw.id},
                                                          {'destination_cidr_block': '10.0.0.0/24',
                                                           'gateway_id': 'local'}])
        routes = [x['gateway_id'] for x in route_table_present_result['changes']['new']['routes']]

        self.assertEqual(set(routes), set(['local', igw.id]))

        route_table_present_result = self.salt_states['boto_vpc.route_table_present'](
                name='test', vpc_name='test', routes=[{'destination_cidr_block': '10.0.0.0/24',
                                                       'gateway_id': 'local'}])

        changes = route_table_present_result['changes']

        old_routes = [x['gateway_id'] for x in changes['old']['routes']]
        self.assertEqual(set(routes), set(old_routes))

        self.assertEqual(changes['new']['routes'][0]['gateway_id'], 'local')
