# -*- coding: utf-8 -*-

# TODO: Update skipped tests to expect dictionary results from the execution
#       module functions.

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import os.path
# pylint: disable=3rd-party-module-not-gated
import pkg_resources
from pkg_resources import DistributionNotFound
# pylint: enable=3rd-party-module-not-gated


# Import Salt libs
from salt.ext import six
from salt.exceptions import SaltInvocationError, CommandExecutionError

# Import Fractus Libs
import fractus.cloudmodules.boto_vpc as boto_vpc
from fractus.cloudmodules.boto_vpc import _maybe_set_name_tag, _maybe_set_tags

# Import Testing Libs
import pytest

boto = pytest.importorskip('boto', minversion='2.8.0')
boto3 = pytest.importorskip('boto3')
exceptions = pytest.importorskip('boto.exception')
moto = pytest.importorskip('moto', minversion='1.0.0')


cidr_block = '10.0.0.0/24'
dhcp_options_parameters = {'domain_name': 'example.com', 'domain_name_servers': ['1.2.3.4'], 'ntp_servers': ['5.6.7.8'],
                           'netbios_name_servers': ['10.0.0.1'], 'netbios_node_type': 2}
network_acl_entry_parameters = ('fake', 100, -1, 'allow', cidr_block)
dhcp_options_parameters.update(pytest.conn_parameters)


def setup_module():
    pytest.helpers.setup_loader({boto_vpc: {'__utils__': pytest.utils}})
    boto_vpc.__init__(pytest.opts)


def _create_vpc(name=None, tags=None):
    '''
    Helper function to create a test vpc
    '''
    conn = boto.vpc.connect_to_region(pytest.region)

    vpc = conn.create_vpc(cidr_block)

    _maybe_set_name_tag(name, vpc)
    _maybe_set_tags(tags, vpc)
    return vpc

def _create_subnet(vpc_id, cidr_block='10.0.0.0/25', name=None, tags=None, availability_zone=None):
    '''
    Helper function to create a test subnet
    '''
    conn = boto.vpc.connect_to_region(pytest.region)

    subnet = conn.create_subnet(vpc_id, cidr_block, availability_zone=availability_zone)
    _maybe_set_name_tag(name, subnet)
    _maybe_set_tags(tags, subnet)
    return subnet

def _create_internet_gateway(vpc_id, name=None, tags=None):
    '''
    Helper function to create a test internet gateway
    '''
    conn = boto.vpc.connect_to_region(pytest.region)

    igw = conn.create_internet_gateway()
    _maybe_set_name_tag(name, igw)
    _maybe_set_tags(tags, igw)
    return igw

def _create_customer_gateway(vpc_id, name=None, tags=None):
    '''
    Helper function to create a test customer gateway
    '''
    conn = boto.vpc.connect_to_region(pytest.region)

    gw = conn.create_customer_gateway(vpc_id)
    _maybe_set_name_tag(name, gw)
    _maybe_set_tags(tags, gw)
    return gw

def _create_dhcp_options(domain_name='example.com', domain_name_servers=None, ntp_servers=None,
                         netbios_name_servers=None, netbios_node_type=2):
    '''
    Helper function to create test dchp options
    '''
    if not netbios_name_servers:
        netbios_name_servers = ['10.0.0.1']
    if not ntp_servers:
        ntp_servers = ['5.6.7.8']
    if not domain_name_servers:
        domain_name_servers = ['1.2.3.4']

    conn = boto.vpc.connect_to_region(pytest.region)

    return conn.create_dhcp_options(domain_name=domain_name, domain_name_servers=domain_name_servers,
                                         ntp_servers=ntp_servers, netbios_name_servers=netbios_name_servers,
                                         netbios_node_type=netbios_node_type)

def _create_network_acl(vpc_id):
    '''
    Helper function to create test network acl
    '''
    conn = boto.vpc.connect_to_region(pytest.region)

    return conn.create_network_acl(vpc_id)

def _create_network_acl_entry(network_acl_id, rule_number, protocol, rule_action, cidr_block, egress=None,
                              icmp_code=None, icmp_type=None, port_range_from=None, port_range_to=None):
    '''
    Helper function to create test network acl entry
    '''
    conn = boto.vpc.connect_to_region(pytest.region)

    return conn.create_network_acl_entry(network_acl_id, rule_number, protocol, rule_action,
                                              cidr_block,
                                              egress=egress,
                                              icmp_code=icmp_code, icmp_type=icmp_type,
                                              port_range_from=port_range_from, port_range_to=port_range_to)

def _create_route_table(vpc_id, name=None, tags=None):
    '''
    Helper function to create a test route table
    '''
    conn = boto.vpc.connect_to_region(pytest.region)

    rtbl = conn.create_route_table(vpc_id)
    _maybe_set_name_tag(name, rtbl)
    _maybe_set_tags(tags, rtbl)
    return rtbl





@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_id_and_a_vpc_exists_the_vpc_exists_method_returns_true(boto_conn):
    '''
    Tests checking vpc existence via id when the vpc already exists
    '''
    vpc = _create_vpc()

    vpc_exists_result = boto_vpc.exists(vpc_id=vpc.id, **pytest.conn_parameters)

    assert vpc_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_id_and_a_vpc_does_not_exist_the_vpc_exists_method_returns_false(boto_conn):
    '''
    Tests checking vpc existence via id when the vpc does not exist
    '''
    _create_vpc()  # Created to ensure that the filters are applied correctly

    vpc_exists_result = boto_vpc.exists(vpc_id='fake', **pytest.conn_parameters)

    assert not vpc_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_name_and_a_vpc_exists_the_vpc_exists_method_returns_true(boto_conn):
    '''
    Tests checking vpc existence via name when vpc exists
    '''
    _create_vpc(name='test')

    vpc_exists_result = boto_vpc.exists(name='test', **pytest.conn_parameters)

    assert vpc_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_name_and_a_vpc_does_not_exist_the_vpc_exists_method_returns_false(boto_conn):
    '''
    Tests checking vpc existence via name when vpc does not exist
    '''
    _create_vpc()  # Created to ensure that the filters are applied correctly

    vpc_exists_result = boto_vpc.exists(name='test', **pytest.conn_parameters)

    assert not vpc_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_tags_and_a_vpc_exists_the_vpc_exists_method_returns_true(boto_conn):
    '''
    Tests checking vpc existence via tag when vpc exists
    '''
    _create_vpc(tags={'test': 'testvalue'})

    vpc_exists_result = boto_vpc.exists(tags={'test': 'testvalue'}, **pytest.conn_parameters)

    assert vpc_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_tags_and_a_vpc_does_not_exist_the_vpc_exists_method_returns_false(boto_conn):
    '''
    Tests checking vpc existence via tag when vpc does not exist
    '''
    _create_vpc()  # Created to ensure that the filters are applied correctly

    vpc_exists_result = boto_vpc.exists(tags={'test': 'testvalue'}, **pytest.conn_parameters)

    assert not vpc_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_cidr_and_a_vpc_exists_the_vpc_exists_method_returns_true(boto_conn):
    '''
    Tests checking vpc existence via cidr when vpc exists
    '''
    _create_vpc()

    vpc_exists_result = boto_vpc.exists(cidr=u'10.0.0.0/24', **pytest.conn_parameters)

    assert vpc_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_vpc_exists_by_cidr_and_a_vpc_does_not_exist_the_vpc_exists_method_returns_false(boto_conn):
    '''
    Tests checking vpc existence via cidr when vpc does not exist
    '''
    _create_vpc()  # Created to ensure that the filters are applied correctly

    vpc_exists_result = boto_vpc.exists(cidr=u'10.10.10.10/24', **pytest.conn_parameters)

    assert not vpc_exists_result['exists']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_checking_if_a_vpc_exists_but_providing_no_filters_the_vpc_exists_method_raises_a_salt_invocation_error(boto_conn):
    '''
    Tests checking vpc existence when no filters are provided
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        boto_vpc.exists(**pytest.conn_parameters)
    assert str(excinfo.value) == 'At least one of the following must be provided: vpc_id, vpc_name, cidr or tags.'

@moto.mock_ec2_deprecated
def test_get_vpc_id_method_when_filtering_by_name(boto_conn):
    '''
    Tests getting vpc id when filtering by name
    '''
    vpc = _create_vpc(name='test')

    get_id_result = boto_vpc.get_id(name='test', **pytest.conn_parameters)

    assert vpc.id == get_id_result['id']

@moto.mock_ec2_deprecated
def test_get_vpc_id_method_when_filtering_by_invalid_name(boto_conn):
    '''
    Tests getting vpc id when filtering by invalid name
    '''
    _create_vpc(name='test')

    get_id_result = boto_vpc.get_id(name='test_fake', **pytest.conn_parameters)

    assert get_id_result['id'] == None

@moto.mock_ec2_deprecated
def test_get_vpc_id_method_when_filtering_by_cidr(boto_conn):
    '''
    Tests getting vpc id when filtering by cidr
    '''
    vpc = _create_vpc()

    get_id_result = boto_vpc.get_id(cidr=u'10.0.0.0/24', **pytest.conn_parameters)

    assert vpc.id == get_id_result['id']

@moto.mock_ec2_deprecated
def test_get_vpc_id_method_when_filtering_by_invalid_cidr(boto_conn):
    '''
    Tests getting vpc id when filtering by invalid cidr
    '''
    _create_vpc()

    get_id_result = boto_vpc.get_id(cidr=u'10.10.10.10/24', **pytest.conn_parameters)

    assert get_id_result['id'] == None

@moto.mock_ec2_deprecated
def test_get_vpc_id_method_when_filtering_by_tags(boto_conn):
    '''
    Tests getting vpc id when filtering by tags
    '''
    vpc = _create_vpc(tags={'test': 'testvalue'})

    get_id_result = boto_vpc.get_id(tags={'test': 'testvalue'}, **pytest.conn_parameters)

    assert vpc.id == get_id_result['id']

@moto.mock_ec2_deprecated
def test_get_vpc_id_method_when_filtering_by_invalid_tags(boto_conn):
    '''
    Tests getting vpc id when filtering by invalid tags
    '''
    _create_vpc(tags={'test': 'testvalue'})

    get_id_result = boto_vpc.get_id(tags={'test': 'fake-testvalue'}, **pytest.conn_parameters)

    assert get_id_result['id'] == None

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_get_vpc_id_method_when_not_providing_filters_raises_a_salt_invocation_error(boto_conn):
    '''
    Tests getting vpc id but providing no filters
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        boto_vpc.get_id(**pytest.conn_parameters)
    assert str(excinfo.value) == 'At least one of the following must be provided: vpc_id, vpc_name, cidr or tags.'

@moto.mock_ec2_deprecated
def test_get_vpc_id_method_when_more_than_one_vpc_is_matched_raises_a_salt_command_execution_error(boto_conn):
    '''
    Tests getting vpc id but providing no filters
    '''
    vpc1 = _create_vpc(name='vpc-test1')
    vpc2 = _create_vpc(name='vpc-test2')

    with pytest.raises(CommandExecutionError) as excinfo:
        boto_vpc.get_id(cidr=u'10.0.0.0/24', **pytest.conn_parameters)
    assert str(excinfo.value) == 'Found more than one VPC matching the criteria.'

@moto.mock_ec2_deprecated
def test_that_when_creating_a_vpc_succeeds_the_create_vpc_method_returns_true(boto_conn):
    '''
    tests True VPC created.
    '''
    vpc_creation_result = boto_vpc.create(cidr_block, **pytest.conn_parameters)

    assert vpc_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_a_vpc_and_specifying_a_vpc_name_succeeds_the_create_vpc_method_returns_true(boto_conn):
    '''
    tests True VPC created.
    '''
    vpc_creation_result = boto_vpc.create(cidr_block, vpc_name='test', **pytest.conn_parameters)

    assert vpc_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_a_vpc_and_specifying_tags_succeeds_the_create_vpc_method_returns_true(boto_conn):
    '''
    tests True VPC created.
    '''
    vpc_creation_result = boto_vpc.create(cidr_block, tags={'test': 'value'}, **pytest.conn_parameters)

    assert vpc_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_creating_a_vpc_fails_the_create_vpc_method_returns_false(boto_conn):
    '''
    tests False VPC not created.
    '''
    with patch('moto.ec2.models.VPCBackend.create_vpc', side_effect=BotoServerError(400, 'Mocked error')):
        vpc_creation_result = boto_vpc.create(cidr_block, **pytest.conn_parameters)
        assert not vpc_creation_result['created']
        assert 'error' in vpc_creation_result

@moto.mock_ec2_deprecated
def test_that_when_deleting_an_existing_vpc_the_delete_vpc_method_returns_true(boto_conn):
    '''
    Tests deleting an existing vpc
    '''
    vpc = _create_vpc()

    vpc_deletion_result = boto_vpc.delete(vpc.id, **pytest.conn_parameters)

    assert vpc_deletion_result

@moto.mock_ec2_deprecated
def test_that_when_deleting_a_non_existent_vpc_the_delete_vpc_method_returns_false(boto_conn):
    '''
    Tests deleting a non-existent vpc
    '''
    delete_vpc_result = boto_vpc.delete('1234', **pytest.conn_parameters)

    assert not delete_vpc_result['deleted']

@moto.mock_ec2_deprecated
def test_that_when_describing_vpc_by_id_it_returns_the_dict_of_properties_returns_true(boto_conn):
    '''
    Tests describing parameters via vpc id if vpc exist
    '''
    is_default = False

    vpc = _create_vpc(name='test', tags={'test': 'testvalue'})

    describe_vpc = boto_vpc.describe(vpc_id=vpc.id, **pytest.conn_parameters)

    vpc_properties = dict(id=vpc.id,
                          cidr_block=six.text_type(cidr_block),
                          is_default=is_default,
                          state=u'available',
                          tags={u'Name': u'test', u'test': u'testvalue'},
                          dhcp_options_id=u'dopt-7a8b9c2d',
                          region=u'us-east-1',
                          instance_tenancy=u'default')

    assert describe_vpc == {'vpc': vpc_properties}

@moto.mock_ec2_deprecated
def test_that_when_describing_vpc_by_id_it_returns_the_dict_of_properties_returns_false(boto_conn):
    '''
    Tests describing parameters via vpc id if vpc does not exist
    '''
    vpc = _create_vpc(name='test', tags={'test': 'testvalue'})

    describe_vpc = boto_vpc.describe(vpc_id='vpc-fake', **pytest.conn_parameters)

    assert not describe_vpc['vpc']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_describing_vpc_by_id_on_connection_error_it_returns_error(boto_conn):
    '''
    Tests describing parameters failure
    '''
    vpc = _create_vpc(name='test', tags={'test': 'testvalue'})

    with patch('moto.ec2.models.VPCBackend.get_all_vpcs',
            side_effect=BotoServerError(400, 'Mocked error')):
        describe_result = boto_vpc.describe(vpc_id=vpc.id, **pytest.conn_parameters)
        assert 'error' in describe_result

@moto.mock_ec2_deprecated
def test_that_when_describing_vpc_but_providing_no_vpc_id_the_describe_method_raises_a_salt_invocation_error(boto_conn):
    '''
    Tests describing vpc without vpc id
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        boto_vpc.describe(vpc_id=None, **pytest.conn_parameters)
    assert str(excinfo.value) == 'A valid vpc id or name needs to be specified.'


@moto.mock_ec2_deprecated
def test_get_subnet_association_single_subnet(boto_conn):
    '''
    tests that given multiple subnet ids in the same VPC that the VPC ID is
    returned. The test is valuable because it uses a string as an argument
    to subnets as opposed to a list.
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)
    subnet_association = boto_vpc.get_subnet_association(subnets=subnet.id,
                                                         **pytest.conn_parameters)
    assert vpc.id == subnet_association['vpc_id']

@moto.mock_ec2_deprecated
def test_get_subnet_association_multiple_subnets_same_vpc(boto_conn):
    '''
    tests that given multiple subnet ids in the same VPC that the VPC ID is
    returned.
    '''
    vpc = _create_vpc()
    subnet_a = _create_subnet(vpc.id, '10.0.0.0/25')
    subnet_b = _create_subnet(vpc.id, '10.0.0.128/25')
    subnet_association = boto_vpc.get_subnet_association([subnet_a.id, subnet_b.id],
                                                         **pytest.conn_parameters)
    assert vpc.id == subnet_association['vpc_id']

@moto.mock_ec2_deprecated
def test_get_subnet_association_multiple_subnets_different_vpc(boto_conn):
    '''
    tests that given multiple subnet ids in different VPCs that False is
    returned.
    '''
    vpc_a = _create_vpc()
    vpc_b = _create_vpc(cidr_block)
    subnet_a = _create_subnet(vpc_a.id, '10.0.0.0/24')
    subnet_b = _create_subnet(vpc_b.id, '10.0.0.0/24')
    subnet_association = boto_vpc.get_subnet_association([subnet_a.id, subnet_b.id],
                                                        **pytest.conn_parameters)
    assert set(subnet_association['vpc_ids']) == set([vpc_a.id, vpc_b.id])

@moto.mock_ec2_deprecated
def test_that_when_creating_a_subnet_succeeds_the_create_subnet_method_returns_true(boto_conn):
    '''
    Tests creating a subnet successfully
    '''
    vpc = _create_vpc()

    subnet_creation_result = boto_vpc.create_subnet(vpc.id, '10.0.0.0/24', **pytest.conn_parameters)

    assert subnet_creation_result['created']
    assert 'id' in subnet_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_a_subnet_and_specifying_a_name_succeeds_the_create_subnet_method_returns_true(boto_conn):
    '''
    Tests creating a subnet successfully when specifying a name
    '''
    vpc = _create_vpc()

    subnet_creation_result = boto_vpc.create_subnet(vpc.id, '10.0.0.0/24', subnet_name='test', **pytest.conn_parameters)

    assert subnet_creation_result['created']

@moto.mock_ec2_deprecated
def test_that_when_creating_a_subnet_and_specifying_tags_succeeds_the_create_subnet_method_returns_true(boto_conn):
    '''
    Tests creating a subnet successfully when specifying a tag
    '''
    vpc = _create_vpc()

    subnet_creation_result = boto_vpc.create_subnet(vpc.id, '10.0.0.0/24', tags={'test': 'testvalue'},
                                                    **pytest.conn_parameters)

    assert subnet_creation_result['created']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_creating_a_subnet_fails_the_create_subnet_method_returns_error(boto_conn):
    '''
    Tests creating a subnet failure
    '''
    vpc = _create_vpc()

    with patch('moto.ec2.models.SubnetBackend.create_subnet', side_effect=BotoServerError(400, 'Mocked error')):
        subnet_creation_result = boto_vpc.create_subnet(vpc.id, '10.0.0.0/24', **pytest.conn_parameters)
        assert 'error' in subnet_creation_result

@moto.mock_ec2_deprecated
def test_that_when_deleting_an_existing_subnet_the_delete_subnet_method_returns_true(boto_conn):
    '''
    Tests deleting an existing subnet
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    subnet_deletion_result = boto_vpc.delete_subnet(subnet_id=subnet.id, **pytest.conn_parameters)

    assert subnet_deletion_result['deleted']

@moto.mock_ec2_deprecated
def test_that_when_deleting_a_non_existent_subnet_the_delete_vpc_method_returns_false(boto_conn):
    '''
    Tests deleting a subnet that doesn't exist
    '''
    delete_subnet_result = boto_vpc.delete_subnet(subnet_id='1234', **pytest.conn_parameters)
    assert 'error' in delete_subnet_result

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_subnet_exists_by_id_the_subnet_exists_method_returns_true(boto_conn):
    '''
    Tests checking if a subnet exists when it does exist
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    subnet_exists_result = boto_vpc.subnet_exists(subnet_id=subnet.id, **pytest.conn_parameters)

    assert subnet_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_a_subnet_does_not_exist_the_subnet_exists_method_returns_false(boto_conn):
    '''
    Tests checking if a subnet exists which doesn't exist
    '''
    subnet_exists_result = boto_vpc.subnet_exists('fake', **pytest.conn_parameters)

    assert not subnet_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_subnet_exists_by_name_the_subnet_exists_method_returns_true(boto_conn):
    '''
    Tests checking subnet existence by name
    '''
    vpc = _create_vpc()
    _create_subnet(vpc.id, name='test')

    subnet_exists_result = boto_vpc.subnet_exists(name='test', **pytest.conn_parameters)

    assert subnet_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_subnet_exists_by_name_the_subnet_does_not_exist_the_subnet_method_returns_false(boto_conn):
    '''
    Tests checking subnet existence by name when it doesn't exist
    '''
    vpc = _create_vpc()
    _create_subnet(vpc.id)

    subnet_exists_result = boto_vpc.subnet_exists(name='test', **pytest.conn_parameters)

    assert not subnet_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_subnet_exists_by_tags_the_subnet_exists_method_returns_true(boto_conn):
    '''
    Tests checking subnet existence by tag
    '''
    vpc = _create_vpc()
    _create_subnet(vpc.id, tags={'test': 'testvalue'})

    subnet_exists_result = boto_vpc.subnet_exists(tags={'test': 'testvalue'}, **pytest.conn_parameters)

    assert subnet_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_checking_if_a_subnet_exists_by_tags_the_subnet_does_not_exist_the_subnet_method_returns_false(boto_conn):
    '''
    Tests checking subnet existence by tag when subnet doesn't exist
    '''
    vpc = _create_vpc()
    _create_subnet(vpc.id)

    subnet_exists_result = boto_vpc.subnet_exists(tags={'test': 'testvalue'}, **pytest.conn_parameters)

    assert not subnet_exists_result['exists']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_checking_if_a_subnet_exists_but_providing_no_filters_the_subnet_exists_method_raises_a_salt_invocation_error(boto_conn):
    '''
    Tests checking subnet existence without any filters
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        boto_vpc.subnet_exists(**pytest.conn_parameters)
    assert str(excinfo.value) == 'At least one of the following must be specified: subnet id, cidr, subnet_name, tags, or zones.'

@pytest.mark.skip('Skip these tests while investigating failures')
@moto.mock_ec2_deprecated
def test_that_describe_subnet_by_id_for_existing_subnet_returns_correct_data(boto_conn):
    '''
    Tests describing a subnet by id.
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    describe_subnet_results = boto_vpc.describe_subnet(region=pytest.region,
                                                       key=pytest.secret_key,
                                                       keyid=pytest.access_key,
                                                       subnet_id=subnet.id)
    assert set(describe_subnet_results['subnet'].keys()) == \
                     set(['id', 'cidr_block', 'availability_zone', 'tags'])

@moto.mock_ec2_deprecated
def test_that_describe_subnet_by_id_for_non_existent_subnet_returns_none(boto_conn):
    '''
    Tests describing a non-existent subnet by id.
    '''
    _create_vpc()

    describe_subnet_results = boto_vpc.describe_subnet(region=pytest.region,
                                                       key=pytest.secret_key,
                                                       keyid=pytest.access_key,
                                                       subnet_id='subnet-a1b2c3')
    assert describe_subnet_results['subnet'] == None

@pytest.mark.skip('Skip these tests while investigating failures')
@moto.mock_ec2_deprecated
def test_that_describe_subnet_by_name_for_existing_subnet_returns_correct_data(boto_conn):
    '''
    Tests describing a subnet by name.
    '''
    vpc = _create_vpc()
    _create_subnet(vpc.id, name='test')

    describe_subnet_results = boto_vpc.describe_subnet(region=pytest.region,
                                                       key=pytest.secret_key,
                                                       keyid=pytest.access_key,
                                                       subnet_name='test')
    assert set(describe_subnet_results['subnet'].keys()) == \
                     set(['id', 'cidr_block', 'availability_zone', 'tags'])

@moto.mock_ec2_deprecated
def test_that_describe_subnet_by_name_for_non_existent_subnet_returns_none(boto_conn):
    '''
    Tests describing a non-existent subnet by id.
    '''
    _create_vpc()

    describe_subnet_results = boto_vpc.describe_subnet(region=pytest.region,
                                                       key=pytest.secret_key,
                                                       keyid=pytest.access_key,
                                                       subnet_name='test')
    assert describe_subnet_results['subnet'] == None

@pytest.mark.skip('Skip these tests while investigating failures')
@moto.mock_ec2_deprecated
def test_that_describe_subnets_by_id_for_existing_subnet_returns_correct_data(boto_conn):
    '''
    Tests describing multiple subnets by id.
    '''
    vpc = _create_vpc()
    subnet1 = _create_subnet(vpc.id)
    subnet2 = _create_subnet(vpc.id)

    describe_subnet_results = boto_vpc.describe_subnets(region=pytest.region,
                                                        key=pytest.secret_key,
                                                        keyid=pytest.access_key,
                                                        subnet_ids=[subnet1.id, subnet2.id])
    assert len(describe_subnet_results['subnets']) == 2
    assert set(describe_subnet_results['subnets'][0].keys()) == \
                     set(['id', 'cidr_block', 'availability_zone', 'tags'])

@pytest.mark.skip('Skip these tests while investigating failures')
@moto.mock_ec2_deprecated
def test_that_describe_subnets_by_name_for_existing_subnets_returns_correct_data(boto_conn):
    '''
    Tests describing multiple subnets by id.
    '''
    vpc = _create_vpc()
    _create_subnet(vpc.id, name='subnet1')
    _create_subnet(vpc.id, name='subnet2')

    describe_subnet_results = boto_vpc.describe_subnets(region=pytest.region,
                                                        key=pytest.secret_key,
                                                        keyid=pytest.access_key,
                                                        subnet_names=['subnet1', 'subnet2'])
    assert len(describe_subnet_results['subnets']) == 2
    assert set(describe_subnet_results['subnets'][0].keys()) == \
                     set(['id', 'cidr_block', 'availability_zone', 'tags'])

@moto.mock_ec2_deprecated
def test_create_subnet_passes_availability_zone(boto_conn):
    '''
    Tests that the availability_zone kwarg is passed on to _create_resource
    '''
    vpc = _create_vpc()
    _create_subnet(vpc.id, name='subnet1', availability_zone='us-east-1a')
    describe_subnet_results = boto_vpc.describe_subnets(region=pytest.region,
                                                        key=pytest.secret_key,
                                                        keyid=pytest.access_key,
                                                        subnet_names=['subnet1'])
    assert describe_subnet_results['subnets'][0]['availability_zone'] == 'us-east-1a'


@moto.mock_ec2_deprecated
def test_that_when_creating_an_internet_gateway_the_create_internet_gateway_method_returns_true(boto_conn):
    '''
    Tests creating an internet gateway successfully (with no vpc id or name)
    '''

    igw_creation_result = boto_vpc.create_internet_gateway(region=pytest.region,
                                                           key=pytest.secret_key,
                                                           keyid=pytest.access_key)
    assert igw_creation_result.get('created')

@moto.mock_ec2_deprecated
def test_that_when_creating_an_internet_gateway_with_non_existent_vpc_the_create_internet_gateway_method_returns_an_error(boto_conn):
    '''
    Tests that creating an internet gateway for a non-existent VPC fails.
    '''

    igw_creation_result = boto_vpc.create_internet_gateway(region=pytest.region,
                                                           key=pytest.secret_key,
                                                           keyid=pytest.access_key,
                                                           vpc_name='non-existent-vpc')
    assert 'error' in igw_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_an_internet_gateway_with_vpc_name_specified_the_create_internet_gateway_method_returns_true(boto_conn):
    '''
    Tests creating an internet gateway with vpc name specified.
    '''

    _create_vpc(name='test-vpc')

    igw_creation_result = boto_vpc.create_internet_gateway(region=pytest.region,
                                                           key=pytest.secret_key,
                                                           keyid=pytest.access_key,
                                                           vpc_name='test-vpc')

    assert igw_creation_result.get('created')

@moto.mock_ec2_deprecated
def test_that_when_creating_an_internet_gateway_with_vpc_id_specified_the_create_internet_gateway_method_returns_true(boto_conn):
    '''
    Tests creating an internet gateway with vpc name specified.
    '''

    vpc = _create_vpc()

    igw_creation_result = boto_vpc.create_internet_gateway(region=pytest.region,
                                                           key=pytest.secret_key,
                                                           keyid=pytest.access_key,
                                                           vpc_id=vpc.id)

    assert igw_creation_result.get('created')


@moto.mock_ec2_deprecated
def test_that_when_creating_an_nat_gateway_the_create_nat_gateway_method_returns_true(boto_conn):
    '''
    Tests creating an nat gateway successfully (with subnet_id specified)
    '''

    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id, name='subnet1', availability_zone='us-east-1a')
    ngw_creation_result = boto_vpc.create_nat_gateway(subnet_id=subnet.id,
                                                      region=pytest.region,
                                                      key=pytest.secret_key,
                                                      keyid=pytest.access_key)
    assert ngw_creation_result.get('created')

@moto.mock_ec2_deprecated
def test_that_when_creating_an_nat_gateway_with_non_existent_subnet_the_create_nat_gateway_method_returns_an_error(boto_conn):
    '''
    Tests that creating an nat gateway for a non-existent subnet fails.
    '''

    ngw_creation_result = boto_vpc.create_nat_gateway(region=pytest.region,
                                                      key=pytest.secret_key,
                                                      keyid=pytest.access_key,
                                                      subnet_name='non-existent-subnet')
    assert 'error' in ngw_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_an_nat_gateway_with_subnet_name_specified_the_create_nat_gateway_method_returns_true(boto_conn):
    '''
    Tests creating an nat gateway with subnet name specified.
    '''

    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id, name='test-subnet', availability_zone='us-east-1a')
    ngw_creation_result = boto_vpc.create_nat_gateway(region=pytest.region,
                                                      key=pytest.secret_key,
                                                      keyid=pytest.access_key,
                                                      subnet_name='test-subnet')

    assert ngw_creation_result.get('created')


@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_a_customer_gateway_the_create_customer_gateway_method_returns_true(boto_conn):
    '''
    Tests creating an internet gateway successfully (with no vpc id or name)
    '''

    gw_creation_result = boto_vpc.create_customer_gateway('ipsec.1', '10.1.1.1', None)
    assert gw_creation_result.get('created')

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_checking_if_a_subnet_exists_by_id_the_subnet_exists_method_returns_true(boto_conn):
    '''
    Tests checking if a subnet exists when it does exist
    '''

    gw_creation_result = boto_vpc.create_customer_gateway('ipsec.1', '10.1.1.1', None)
    gw_exists_result = boto_vpc.customer_gateway_exists(customer_gateway_id=gw_creation_result['id'])
    assert gw_exists_result['exists']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_a_subnet_does_not_exist_the_subnet_exists_method_returns_false(boto_conn):
    '''
    Tests checking if a subnet exists which doesn't exist
    '''
    gw_exists_result = boto_vpc.customer_gateway_exists('fake')
    assert not gw_exists_result['exists']


@moto.mock_ec2_deprecated
def test_that_when_creating_dhcp_options_succeeds_the_create_dhcp_options_method_returns_true(boto_conn):
    '''
    Tests creating dhcp options successfully
    '''
    dhcp_options_creation_result = boto_vpc.create_dhcp_options(**dhcp_options_parameters)

    assert dhcp_options_creation_result['created']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_dhcp_options_and_specifying_a_name_succeeds_the_create_dhcp_options_method_returns_true(boto_conn):
    '''
    Tests creating dchp options with name successfully
    '''
    dhcp_options_creation_result = boto_vpc.create_dhcp_options(dhcp_options_name='test',
                                                                **dhcp_options_parameters)

    assert dhcp_options_creation_result['created']

@moto.mock_ec2_deprecated
def test_that_when_creating_dhcp_options_and_specifying_tags_succeeds_the_create_dhcp_options_method_returns_true(boto_conn):
    '''
    Tests creating dchp options with tag successfully
    '''
    dhcp_options_creation_result = boto_vpc.create_dhcp_options(tags={'test': 'testvalue'},
                                                                **dhcp_options_parameters)

    assert dhcp_options_creation_result['created']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_creating_dhcp_options_fails_the_create_dhcp_options_method_returns_error(boto_conn):
    '''
    Tests creating dhcp options failure
    '''
    with patch('moto.ec2.models.DHCPOptionsSetBackend.create_dhcp_options',
               side_effect=BotoServerError(400, 'Mocked error')):
        r = dhcp_options_creation_result = boto_vpc.create_dhcp_options(**dhcp_options_parameters)
        assert 'error' in r

@moto.mock_ec2_deprecated
def test_that_when_associating_an_existing_dhcp_options_set_to_an_existing_vpc_the_associate_dhcp_options_method_returns_true(boto_conn):
    '''
    Tests associating existing dchp options successfully
    '''
    vpc = _create_vpc()
    dhcp_options = _create_dhcp_options()

    dhcp_options_association_result = boto_vpc.associate_dhcp_options_to_vpc(dhcp_options.id, vpc.id,
                                                                             **pytest.conn_parameters)

    assert dhcp_options_association_result['associated']

@moto.mock_ec2_deprecated
def test_that_when_associating_a_non_existent_dhcp_options_set_to_an_existing_vpc_the_associate_dhcp_options_method_returns_error(
        boto_conn):
    '''
    Tests associating non-existanct dhcp options successfully
    '''
    vpc = _create_vpc()

    dhcp_options_association_result = boto_vpc.associate_dhcp_options_to_vpc('fake', vpc.id, **pytest.conn_parameters)

    assert 'error' in dhcp_options_association_result

@moto.mock_ec2_deprecated
def test_that_when_associating_an_existing_dhcp_options_set_to_a_non_existent_vpc_the_associate_dhcp_options_method_returns_false(
        boto_conn):
    '''
    Tests associating existing dhcp options to non-existence vpc
    '''
    dhcp_options = _create_dhcp_options()

    dhcp_options_association_result = boto_vpc.associate_dhcp_options_to_vpc(dhcp_options.id, 'fake',
                                                                             **pytest.conn_parameters)

    assert 'error' in dhcp_options_association_result

@moto.mock_ec2_deprecated
def test_that_when_creating_dhcp_options_set_to_an_existing_vpc_succeeds_the_associate_new_dhcp_options_method_returns_true(
        boto_conn):
    '''
    Tests creation/association of dchp options to an existing vpc successfully
    '''
    vpc = _create_vpc()

    dhcp_creation_result = boto_vpc.create_dhcp_options(vpc_id=vpc.id, **dhcp_options_parameters)

    assert dhcp_creation_result['created']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_creating_and_associating_dhcp_options_set_to_an_existing_vpc_fails_creating_the_dhcp_options_the_associate_new_dhcp_options_method_raises_exception(
        boto_conn):
    '''
    Tests creation failure during creation/association of dchp options to an existing vpc
    '''
    vpc = _create_vpc()

    with patch('moto.ec2.models.DHCPOptionsSetBackend.create_dhcp_options',
               side_effect=BotoServerError(400, 'Mocked error')):
        r = boto_vpc.associate_new_dhcp_options_to_vpc(vpc.id, **dhcp_options_parameters)
        assert 'error' in r

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_creating_and_associating_dhcp_options_set_to_an_existing_vpc_fails_associating_the_dhcp_options_the_associate_new_dhcp_options_method_raises_exception(boto_conn):
    '''
    Tests association failure during creation/association of dchp options to existing vpc
    '''
    vpc = _create_vpc()

    with patch('moto.ec2.models.DHCPOptionsSetBackend.associate_dhcp_options',
               side_effect=BotoServerError(400, 'Mocked error')):
        r = boto_vpc.associate_new_dhcp_options_to_vpc(vpc.id, **dhcp_options_parameters)
        assert 'error' in r

@moto.mock_ec2_deprecated
def test_that_when_creating_dhcp_options_set_to_a_non_existent_vpc_the_dhcp_options_the_associate_new_dhcp_options_method_returns_false(
        boto_conn):
    '''
    Tests creation/association of dhcp options to non-existent vpc
    '''

    r = boto_vpc.create_dhcp_options(vpc_name='fake', **dhcp_options_parameters)
    assert 'error' in r

@moto.mock_ec2_deprecated
def test_that_when_dhcp_options_exists_the_dhcp_options_exists_method_returns_true(boto_conn):
    '''
    Tests existence of dhcp options successfully
    '''
    dhcp_options = _create_dhcp_options()

    dhcp_options_exists_result = boto_vpc.dhcp_options_exists(dhcp_options.id, **pytest.conn_parameters)

    assert dhcp_options_exists_result['exists']

@moto.mock_ec2_deprecated
def test_that_when_dhcp_options_do_not_exist_the_dhcp_options_exists_method_returns_false(boto_conn):
    '''
    Tests existence of dhcp options failure
    '''
    r = boto_vpc.dhcp_options_exists('fake', **pytest.conn_parameters)
    assert not r['exists']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_checking_if_dhcp_options_exists_but_providing_no_filters_the_dhcp_options_exists_method_raises_a_salt_invocation_error(boto_conn):
    '''
    Tests checking dhcp option existence with no filters
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        boto_vpc.dhcp_options_exists(**pytest.conn_parameters)
    assert str(excinfo.value) == 'At least one of the following must be provided: id, name, or tags.'


@moto.mock_ec2_deprecated
def test_that_when_creating_network_acl_for_an_existing_vpc_the_create_network_acl_method_returns_true(boto_conn):
    '''
    Tests creation of network acl with existing vpc
    '''
    vpc = _create_vpc()

    network_acl_creation_result = boto_vpc.create_network_acl(vpc.id, **pytest.conn_parameters)

    assert network_acl_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_network_acl_for_an_existing_vpc_and_specifying_a_name_the_create_network_acl_method_returns_true(
        boto_conn):
    '''
    Tests creation of network acl via name with an existing vpc
    '''
    vpc = _create_vpc()

    network_acl_creation_result = boto_vpc.create_network_acl(vpc.id, network_acl_name='test', **pytest.conn_parameters)

    assert network_acl_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_network_acl_for_an_existing_vpc_and_specifying_tags_the_create_network_acl_method_returns_true(
        boto_conn):
    '''
    Tests creation of network acl via tags with an existing vpc
    '''
    vpc = _create_vpc()

    network_acl_creation_result = boto_vpc.create_network_acl(vpc.id, tags={'test': 'testvalue'}, **pytest.conn_parameters)

    assert network_acl_creation_result

@moto.mock_ec2_deprecated
def test_that_when_creating_network_acl_for_a_non_existent_vpc_the_create_network_acl_method_returns_an_error(boto_conn):
    '''
    Tests creation of network acl with a non-existent vpc
    '''
    network_acl_creation_result = boto_vpc.create_network_acl('fake', **pytest.conn_parameters)

    assert 'error' in network_acl_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_network_acl_fails_the_create_network_acl_method_returns_false(boto_conn):
    '''
    Tests creation of network acl failure
    '''
    vpc = _create_vpc()

    with patch('moto.ec2.models.NetworkACLBackend.create_network_acl',
               side_effect=BotoServerError(400, 'Mocked error')):
        network_acl_creation_result = boto_vpc.create_network_acl(vpc.id, **pytest.conn_parameters)

    assert not network_acl_creation_result

@moto.mock_ec2_deprecated
def test_that_when_deleting_an_existing_network_acl_the_delete_network_acl_method_returns_true(boto_conn):
    '''
    Tests deletion of existing network acl successfully
    '''
    vpc = _create_vpc()
    network_acl = _create_network_acl(vpc.id)

    network_acl_deletion_result = boto_vpc.delete_network_acl(network_acl.id, **pytest.conn_parameters)

    assert network_acl_deletion_result

@moto.mock_ec2_deprecated
def test_that_when_deleting_a_non_existent_network_acl_the_delete_network_acl_method_returns_an_error(boto_conn):
    '''
    Tests deleting a non-existent network acl
    '''
    network_acl_deletion_result = boto_vpc.delete_network_acl('fake', **pytest.conn_parameters)

    assert 'error' in network_acl_deletion_result

@moto.mock_ec2_deprecated
def test_that_when_a_network_acl_exists_the_network_acl_exists_method_returns_true(boto_conn):
    '''
    Tests existence of network acl
    '''
    vpc = _create_vpc()
    network_acl = _create_network_acl(vpc.id)

    network_acl_deletion_result = boto_vpc.network_acl_exists(network_acl.id, **pytest.conn_parameters)

    assert network_acl_deletion_result

@moto.mock_ec2_deprecated
def test_that_when_a_network_acl_does_not_exist_the_network_acl_exists_method_returns_false(boto_conn):
    '''
    Tests checking network acl does not exist
    '''
    network_acl_deletion_result = boto_vpc.network_acl_exists('fake', **pytest.conn_parameters)

    assert not network_acl_deletion_result['exists']

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_checking_if_network_acl_exists_but_providing_no_filters_the_network_acl_exists_method_raises_a_salt_invocation_error(boto_conn):
    '''
    Tests checking existence of network acl with no filters
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        boto_vpc.dhcp_options_exists(**pytest.conn_parameters)
    assert str(excinfo.value) == 'At least one of the following must be provided: id, name, or tags.'

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_a_network_acl_entry_successfully_the_create_network_acl_entry_method_returns_true(boto_conn):
    '''
    Tests creating network acl successfully
    '''
    vpc = _create_vpc()
    network_acl = _create_network_acl(vpc.id)

    network_acl_entry_creation_result = boto_vpc.create_network_acl_entry(network_acl.id,
                                                                          *network_acl_entry_parameters,
                                                                          **pytest.conn_parameters)

    assert network_acl_entry_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_a_network_acl_entry_for_a_non_existent_network_acl_the_create_network_acl_entry_method_returns_false(
        boto_conn):
    '''
    Tests creating network acl entry for non-existent network acl
    '''
    network_acl_entry_creation_result = boto_vpc.create_network_acl_entry(*network_acl_entry_parameters,
                                                                          **pytest.conn_parameters)

    assert not network_acl_entry_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_replacing_a_network_acl_entry_successfully_the_replace_network_acl_entry_method_returns_true(
        boto_conn):
    '''
    Tests replacing network acl entry successfully
    '''
    vpc = _create_vpc()
    network_acl = _create_network_acl(vpc.id)
    _create_network_acl_entry(network_acl.id, *network_acl_entry_parameters)

    network_acl_entry_creation_result = boto_vpc.replace_network_acl_entry(network_acl.id,
                                                                           *network_acl_entry_parameters,
                                                                           **pytest.conn_parameters)

    assert network_acl_entry_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_replacing_a_network_acl_entry_for_a_non_existent_network_acl_the_replace_network_acl_entry_method_returns_false(
        boto_conn):
    '''
    Tests replacing a network acl entry for a non-existent network acl
    '''
    network_acl_entry_creation_result = boto_vpc.create_network_acl_entry(*network_acl_entry_parameters,
                                                                          **pytest.conn_parameters)
    assert not network_acl_entry_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_deleting_an_existing_network_acl_entry_the_delete_network_acl_entry_method_returns_true(boto_conn):
    '''
    Tests deleting existing network acl entry successfully
    '''
    vpc = _create_vpc()
    network_acl = _create_network_acl(vpc.id)
    network_acl_entry = _create_network_acl_entry(network_acl.id, *network_acl_entry_parameters)

    network_acl_entry_deletion_result = boto_vpc.delete_network_acl_entry(network_acl_entry.id, 100,
                                                                          **pytest.conn_parameters)

    assert network_acl_entry_deletion_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_deleting_a_non_existent_network_acl_entry_the_delete_network_acl_entry_method_returns_false(
        boto_conn):
    '''
    Tests deleting a non-existent network acl entry
    '''
    network_acl_entry_deletion_result = boto_vpc.delete_network_acl_entry('fake', 100,
                                                                          **pytest.conn_parameters)

    assert not network_acl_entry_deletion_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_associating_an_existing_network_acl_to_an_existing_subnet_the_associate_network_acl_method_returns_true(
        boto_conn):
    '''
    Tests association of existing network acl to existing subnet successfully
    '''
    vpc = _create_vpc()
    network_acl = _create_network_acl(vpc.id)
    subnet = _create_subnet(vpc.id)

    network_acl_association_result = boto_vpc.associate_network_acl_to_subnet(network_acl.id, subnet.id,
                                                                              **pytest.conn_parameters)

    assert network_acl_association_result

@moto.mock_ec2_deprecated
def test_that_when_associating_a_non_existent_network_acl_to_an_existing_subnet_the_associate_network_acl_method_returns_an_error(
        boto_conn):
    '''
    Tests associating a non-existent network acl to existing subnet failure
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    network_acl_association_result = boto_vpc.associate_network_acl_to_subnet('fake', subnet.id,
                                                                              **pytest.conn_parameters)

    assert 'error' in network_acl_association_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_associating_an_existing_network_acl_to_a_non_existent_subnet_the_associate_network_acl_method_returns_false(
        boto_conn):
    '''
    Tests associating an existing network acl to a non-existent subnet
    '''
    vpc = _create_vpc()
    network_acl = _create_network_acl(vpc.id)

    network_acl_association_result = boto_vpc.associate_network_acl_to_subnet(network_acl.id, 'fake',
                                                                              **pytest.conn_parameters)

    assert not network_acl_association_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_and_associating_a_network_acl_to_a_subnet_succeeds_the_associate_new_network_acl_to_subnet_method_returns_true(
        boto_conn):
    '''
    Tests creating/associating a network acl to a subnet to a new network
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    network_acl_creation_and_association_result = boto_vpc.associate_new_network_acl_to_subnet(vpc.id, subnet.id,
                                                                                               **pytest.conn_parameters)

    assert network_acl_creation_and_association_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_and_associating_a_network_acl_to_a_subnet_and_specifying_a_name_succeeds_the_associate_new_network_acl_to_subnet_method_returns_true(
        boto_conn):
    '''
    Tests creation/association of a network acl to subnet via name successfully
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    network_acl_creation_and_association_result = boto_vpc.associate_new_network_acl_to_subnet(vpc.id, subnet.id,
                                                                                               network_acl_name='test',
                                                                                               **pytest.conn_parameters)

    assert network_acl_creation_and_association_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_and_associating_a_network_acl_to_a_subnet_and_specifying_tags_succeeds_the_associate_new_network_acl_to_subnet_method_returns_true(
        boto_conn):
    '''
    Tests creating/association of a network acl to a subnet via tag successfully
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    network_acl_creation_and_association_result = boto_vpc.associate_new_network_acl_to_subnet(vpc.id, subnet.id,
                                                                                               tags={
                                                                                                   'test': 'testvalue'},
                                                                                               **pytest.conn_parameters)

    assert network_acl_creation_and_association_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_and_associating_a_network_acl_to_a_non_existent_subnet_the_associate_new_network_acl_to_subnet_method_returns_false(
        boto_conn):
    '''
    Tests creation/association of a network acl to a non-existent vpc
    '''
    vpc = _create_vpc()

    network_acl_creation_and_association_result = boto_vpc.associate_new_network_acl_to_subnet(vpc.id, 'fake',
                                                                                               **pytest.conn_parameters)

    assert not network_acl_creation_and_association_result

@moto.mock_ec2_deprecated
def test_that_when_creating_a_network_acl_to_a_non_existent_vpc_the_associate_new_network_acl_to_subnet_method_returns_an_error(
        boto_conn):
    '''
    Tests creation/association of network acl to a non-existent subnet
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    network_acl_creation_result = boto_vpc.create_network_acl(vpc_name='fake', subnet_id=subnet.id, **pytest.conn_parameters)

    assert 'error' in network_acl_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_disassociating_network_acl_succeeds_the_disassociate_network_acl_method_should_return_true(boto_conn):
    '''
    Tests disassociation of network acl success
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    dhcp_disassociate_result = boto_vpc.disassociate_network_acl(subnet.id, vpc_id=vpc.id, **pytest.conn_parameters)

    assert dhcp_disassociate_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_disassociating_network_acl_for_a_non_existent_vpc_the_disassociate_network_acl_method_should_return_false(
        boto_conn):
    '''
    Tests disassociation of network acl from non-existent vpc
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    dhcp_disassociate_result = boto_vpc.disassociate_network_acl(subnet.id, vpc_id='fake', **pytest.conn_parameters)

    assert not dhcp_disassociate_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_disassociating_network_acl_for_a_non_existent_subnet_the_disassociate_network_acl_method_should_return_false(
        boto_conn):
    '''
    Tests disassociation of network acl from non-existent subnet
    '''
    vpc = _create_vpc()

    dhcp_disassociate_result = boto_vpc.disassociate_network_acl('fake', vpc_id=vpc.id, **pytest.conn_parameters)

    assert not dhcp_disassociate_result


@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_a_route_table_succeeds_the_create_route_table_method_returns_true(boto_conn):
    '''
    Tests creating route table successfully
    '''
    vpc = _create_vpc()

    route_table_creation_result = boto_vpc.create_route_table(vpc.id, **pytest.conn_parameters)

    assert route_table_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_a_route_table_on_a_non_existent_vpc_the_create_route_table_method_returns_false(boto_conn):
    '''
    Tests creating route table on a non-existent vpc
    '''
    route_table_creation_result = boto_vpc.create_route_table('fake', **pytest.conn_parameters)

    assert route_table_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_deleting_a_route_table_succeeds_the_delete_route_table_method_returns_true(boto_conn):
    '''
    Tests deleting route table successfully
    '''
    vpc = _create_vpc()
    route_table = _create_route_table(vpc.id)

    route_table_deletion_result = boto_vpc.delete_route_table(route_table.id, **pytest.conn_parameters)

    assert route_table_deletion_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_deleting_a_non_existent_route_table_the_delete_route_table_method_returns_false(boto_conn):
    '''
    Tests deleting non-existent route table
    '''
    route_table_deletion_result = boto_vpc.delete_route_table('fake', **pytest.conn_parameters)

    assert not route_table_deletion_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_route_table_exists_the_route_table_exists_method_returns_true(boto_conn):
    '''
    Tests existence of route table success
    '''
    vpc = _create_vpc()
    route_table = _create_route_table(vpc.id)

    route_table_existence_result = boto_vpc.route_table_exists(route_table.id, **pytest.conn_parameters)

    assert route_table_existence_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_route_table_does_not_exist_the_route_table_exists_method_returns_false(boto_conn):
    '''
    Tests existence of route table failure
    '''
    route_table_existence_result = boto_vpc.route_table_exists('fake', **pytest.conn_parameters)

    assert not route_table_existence_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Disabled pending https://github.com/spulec/moto/issues/493')
def test_that_when_checking_if_a_route_table_exists_but_providing_no_filters_the_route_table_exists_method_raises_a_salt_invocation_error(boto_conn):
    '''
    Tests checking route table without filters
    '''
    with pytest.raises(SaltInvocationError) as excinfo:
        boto_vpc.dhcp_options_exists(**pytest.conn_parameters)
    assert str(excinfo.value) == 'At least one of the following must be provided: id, name, or tags.'

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_associating_a_route_table_succeeds_the_associate_route_table_method_should_return_the_association_id(
        boto_conn):
    '''
    Tests associating route table successfully
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)
    route_table = _create_route_table(vpc.id)

    association_id = boto_vpc.associate_route_table(route_table.id, subnet.id, **pytest.conn_parameters)

    assert association_id

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_associating_a_route_table_with_a_non_existent_route_table_the_associate_route_table_method_should_return_false(
        boto_conn):
    '''
    Tests associating of route table to non-existent route table
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)

    association_id = boto_vpc.associate_route_table('fake', subnet.id, **pytest.conn_parameters)

    assert not association_id

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_associating_a_route_table_with_a_non_existent_subnet_the_associate_route_table_method_should_return_false(
        boto_conn):
    '''
    Tests associating of route table with non-existent subnet
    '''
    vpc = _create_vpc()
    route_table = _create_route_table(vpc.id)

    association_id = boto_vpc.associate_route_table(route_table.id, 'fake', **pytest.conn_parameters)

    assert not association_id

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_disassociating_a_route_table_succeeds_the_disassociate_route_table_method_should_return_true(
        boto_conn):
    '''
    Tests disassociation of a route
    '''
    vpc = _create_vpc()
    subnet = _create_subnet(vpc.id)
    route_table = _create_route_table(vpc.id)

    association_id = _associate_route_table(route_table.id, subnet.id)

    dhcp_disassociate_result = boto_vpc.disassociate_route_table(association_id, **pytest.conn_parameters)

    assert dhcp_disassociate_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_a_route_succeeds_the_create_route_method_should_return_true(boto_conn):
    '''
    Tests successful creation of a route
    '''
    vpc = _create_vpc()
    route_table = _create_route_table(vpc.id)

    route_creation_result = boto_vpc.create_route(route_table.id, cidr_block, **pytest.conn_parameters)

    assert route_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_creating_a_route_with_a_non_existent_route_table_the_create_route_method_should_return_false(
        boto_conn):
    '''
    Tests creation of route on non-existent route table
    '''
    route_creation_result = boto_vpc.create_route('fake', cidr_block, **pytest.conn_parameters)

    assert not route_creation_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_deleting_a_route_succeeds_the_delete_route_method_should_return_true(boto_conn):
    '''
    Tests deleting route from route table
    '''
    vpc = _create_vpc()
    route_table = _create_route_table(vpc.id)

    route_deletion_result = boto_vpc.delete_route(route_table.id, cidr_block, **pytest.conn_parameters)

    assert route_deletion_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_deleting_a_route_with_a_non_existent_route_table_the_delete_route_method_should_return_false(
        boto_conn):
    '''
    Tests deleting route from a non-existent route table
    '''
    route_deletion_result = boto_vpc.delete_route('fake', cidr_block, **pytest.conn_parameters)

    assert not route_deletion_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_replacing_a_route_succeeds_the_replace_route_method_should_return_true(boto_conn):
    '''
    Tests replacing route successfully
    '''
    vpc = _create_vpc()
    route_table = _create_route_table(vpc.id)

    route_replacing_result = boto_vpc.replace_route(route_table.id, cidr_block, **pytest.conn_parameters)

    assert route_replacing_result

@moto.mock_ec2_deprecated
@pytest.mark.skip('Moto has not implemented this feature. Skipping for now.')
def test_that_when_replacing_a_route_with_a_non_existent_route_table_the_replace_route_method_should_return_false(
        boto_conn):
    '''
    Tests replacing a route when the route table doesn't exist
    '''
    route_replacing_result = boto_vpc.replace_route('fake', cidr_block, **pytest.conn_parameters)

    assert not route_replacing_result


@moto.mock_ec2_deprecated
def test_request_vpc_peering_connection(boto_conn):
    '''
    Run with 2 vpc ids and returns a message
    '''
    my_vpc = _create_vpc()
    other_vpc = _create_vpc()
    assert 'msg' in boto_vpc.request_vpc_peering_connection(
        name='my_peering',
        requester_vpc_id=my_vpc.id,
        peer_vpc_id=other_vpc.id,
        **pytest.conn_parameters)

@moto.mock_ec2_deprecated
def test_raises_error_if_both_vpc_name_and_vpc_id_are_specified(boto_conn):
    '''
    Must specify only one
    '''
    my_vpc = _create_vpc()
    other_vpc = _create_vpc()
    with pytest.raises(SaltInvocationError):
        boto_vpc.request_vpc_peering_connection(name='my_peering',
                                                requester_vpc_id=my_vpc.id,
                                                requester_vpc_name='foobar',
                                                peer_vpc_id=other_vpc.id,
                                                **pytest.conn_parameters)

    boto_vpc.request_vpc_peering_connection(name='my_peering',
                                            requester_vpc_name='my_peering',
                                            peer_vpc_id=other_vpc.id,
                                            **pytest.conn_parameters)
