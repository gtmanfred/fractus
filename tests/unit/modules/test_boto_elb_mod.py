# -*- coding: utf-8 -*-

# import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import logging
from copy import deepcopy
import pkg_resources
import os.path

# Import Fractus Libs
import fractus.loader
import fractus.cloudmodules.boto_elb as boto_elb

# Import Testing Libs
import pytest

log = logging.getLogger(__name__)

region = 'us-east-1'
access_key = 'GKTADJGHEIQSXMKKRBJ08H'
secret_key = 'askdjghsdfjkghWupUjasdflkdfklgjsdfjajkghs'
conn_parameters = {'region': region, 'key': access_key, 'keyid': secret_key,
                   'profile': {}}
boto_conn_parameters = {'aws_access_key_id': access_key,
                        'aws_secret_access_key': secret_key}
instance_parameters = {'instance_type': 't1.micro'}

moto = pytest.importorskip('moto', minversion='1.0.1')
boto = pytest.importorskip('boto')
elb = pytest.importorskip('boto.ec2.elb')


def setup_module():
    pytest.helpers.setup_loader({
        boto_elb: {
            '__opts__': pytest.opts,
            '__utils__': pytest.utils,
            '__salt__': pytest.modules,
        },
    })
    boto_elb.__virtual__()

@moto.mock_ec2_deprecated
@moto.mock_elb_deprecated
def test_register_instances_valid_id_result_true():
    '''
    tests that given a valid instance id and valid ELB that
    register_instances returns True.
    '''
    conn_ec2 = boto.ec2.connect_to_region(region, **boto_conn_parameters)
    conn_elb = elb.connect_to_region(region,
                                              **boto_conn_parameters)
    zones = [zone.name for zone in conn_ec2.get_all_zones()]
    elb_name = 'TestRegisterInstancesValidIdResult'
    conn_elb.create_load_balancer(elb_name, zones, [(80, 80, 'http')])
    reservations = conn_ec2.run_instances('ami-08389d60')
    register_result = boto_elb.register_instances(elb_name,
                                                  reservations.instances[0].id,
                                                  **conn_parameters)
    assert register_result is True

@moto.mock_ec2_deprecated
@moto.mock_elb_deprecated
def test_register_instances_valid_id_string():
    '''
    tests that given a string containing a instance id and valid ELB that
    register_instances adds the given instance to an ELB
    '''
    conn_ec2 = boto.ec2.connect_to_region(region, **boto_conn_parameters)
    conn_elb = elb.connect_to_region(region,
                                              **boto_conn_parameters)
    zones = [zone.name for zone in conn_ec2.get_all_zones()]
    elb_name = 'TestRegisterInstancesValidIdResult'
    conn_elb.create_load_balancer(elb_name, zones, [(80, 80, 'http')])
    reservations = conn_ec2.run_instances('ami-08389d60')
    boto_elb.register_instances(elb_name, reservations.instances[0].id,
                                **conn_parameters)
    load_balancer_refreshed = conn_elb.get_all_load_balancers(elb_name)[0]
    registered_instance_ids = [instance.id for instance in
                               load_balancer_refreshed.instances]

    log.debug(load_balancer_refreshed.instances)
    assert [reservations.instances[0].id] == registered_instance_ids

@moto.mock_ec2_deprecated
@moto.mock_elb_deprecated
def test_deregister_instances_valid_id_result_true():
    '''
    tests that given an valid id the boto_elb deregister_instances method
    removes exactly one of a number of ELB registered instances
    '''
    conn_ec2 = boto.ec2.connect_to_region(region, **boto_conn_parameters)
    conn_elb = elb.connect_to_region(region,
                                              **boto_conn_parameters)
    zones = [zone.name for zone in conn_ec2.get_all_zones()]
    elb_name = 'TestDeregisterInstancesValidIdResult'
    load_balancer = conn_elb.create_load_balancer(elb_name, zones,
                                                  [(80, 80, 'http')])
    reservations = conn_ec2.run_instances('ami-08389d60')
    load_balancer.register_instances(reservations.instances[0].id)
    deregister_result = boto_elb.deregister_instances(elb_name,
                                                      reservations.instances[0].id,
                                                      **conn_parameters)
    assert deregister_result is True

@moto.mock_ec2_deprecated
@moto.mock_elb_deprecated
def test_deregister_instances_valid_id_string():
    '''
    tests that given an valid id the boto_elb deregister_instances method
    removes exactly one of a number of ELB registered instances
    '''
    conn_ec2 = boto.ec2.connect_to_region(region, **boto_conn_parameters)
    conn_elb = elb.connect_to_region(region,
                                              **boto_conn_parameters)
    zones = [zone.name for zone in conn_ec2.get_all_zones()]
    elb_name = 'TestDeregisterInstancesValidIdString'
    load_balancer = conn_elb.create_load_balancer(elb_name, zones,
                                                  [(80, 80, 'http')])
    reservations = conn_ec2.run_instances('ami-08389d60', min_count=2)
    all_instance_ids = [instance.id for instance in reservations.instances]
    load_balancer.register_instances(all_instance_ids)
    boto_elb.deregister_instances(elb_name, reservations.instances[0].id,
                                  **conn_parameters)
    load_balancer_refreshed = conn_elb.get_all_load_balancers(elb_name)[0]
    expected_instances = deepcopy(all_instance_ids)
    expected_instances.remove(reservations.instances[0].id)
    actual_instances = [instance.id for instance in
                        load_balancer_refreshed.instances]
    assert actual_instances == expected_instances

@moto.mock_ec2_deprecated
@moto.mock_elb_deprecated
def test_deregister_instances_valid_id_list():
    '''
    tests that given an valid ids in the form of a list that the boto_elb
    deregister_instances all members of the given list
    '''
    conn_ec2 = boto.ec2.connect_to_region(region, **boto_conn_parameters)
    conn_elb = elb.connect_to_region(region,
                                              **boto_conn_parameters)
    zones = [zone.name for zone in conn_ec2.get_all_zones()]
    elb_name = 'TestDeregisterInstancesValidIdList'
    load_balancer = conn_elb.create_load_balancer(elb_name, zones,
                                                  [(80, 80, 'http')])
    reservations = conn_ec2.run_instances('ami-08389d60', min_count=3)
    all_instance_ids = [instance.id for instance in reservations.instances]
    load_balancer.register_instances(all_instance_ids)
    # reservations.instances[:-1] refers to all instances except list
    # instance
    deregister_instances = [instance.id for instance in
                            reservations.instances[:-1]]
    expected_instances = [reservations.instances[-1].id]
    boto_elb.deregister_instances(elb_name, deregister_instances,
                                  **conn_parameters)
    load_balancer_refreshed = conn_elb.get_all_load_balancers(elb_name)[0]
    actual_instances = [instance.id for instance in
                        load_balancer_refreshed.instances]
    assert actual_instances == expected_instances
