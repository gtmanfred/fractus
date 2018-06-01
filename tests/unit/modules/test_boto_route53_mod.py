# -*- coding: utf-8 -*-

# import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import logging
import os.path

# Import Fractus Libs
import fractus.loader
import fractus.cloudmodules.boto_route53 as boto_route53

# Import Testing Libs
import pytest

log = logging.getLogger(__name__)

moto = pytest.importorskip('moto', minversion='1.0.1')
boto = pytest.importorskip('boto')


def setup_module():
    pytest.opts['route53.keyid'] = 'GKTADJGHEIQSXMKKRBJ08H'
    pytest.opts['route53.key'] = 'askdjghsdfjkghWupUjasdflkdfklgjsdfjajkghs'
    pytest.helpers.setup_loader({
        boto_route53: {
            '__opts__': pytest.opts,
            '__utils__': pytest.utils,
            '__salt__': pytest.modules
        },
    })
    boto_route53.__virtual__()
    boto_route53.__init__(pytest.opts)


@moto.mock_route53_deprecated
def test_create_healthcheck():
    '''
    tests that given a valid instance id and valid ELB that
    register_instances returns True.
    '''
    expected = {
        'result': {
            'CreateHealthCheckResponse': {
                'HealthCheck': {
                    'HealthCheckConfig': {
                        'FailureThreshold': '3',
                        'IPAddress': '10.0.0.1',
                        'ResourcePath': '/',
                        'RequestInterval': '30',
                        'Type': 'HTTPS',
                        'Port': '443',
                        'FullyQualifiedDomainName': 'blog.saltstack.furniture',
                    },
                    'HealthCheckVersion': '1',
                },
            },
        },
    }
    healthcheck = boto_route53.create_healthcheck(
        '10.0.0.1',
        fqdn='blog.saltstack.furniture',
        hc_type='HTTPS',
        port=443,
        resource_path='/',
    )
    del healthcheck['result']['CreateHealthCheckResponse']['HealthCheck']['CallerReference']
    del healthcheck['result']['CreateHealthCheckResponse']['HealthCheck']['Id']
    assert healthcheck == expected
