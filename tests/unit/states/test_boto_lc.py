# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Jayesh Kariya <jayeshk@saltstack.com>`
'''
# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals

# Import Salt Libs
from salt.exceptions import SaltInvocationError

# Import Fractus Libs
import fractus.cloudstates.boto_lc as boto_lc

# Import Testing Libs
import pytest
from mock import MagicMock, patch


def setup_module():
    pytest.helpers.setup_loader({boto_lc: {}})

# 'present' function tests: 1

def test_present():
    '''
    Test to ensure the launch configuration exists.
    '''
    name = 'mylc'
    image_id = 'ami-0b9c9f62'

    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': ''}

    pytest.raises(SaltInvocationError, boto_lc.present, name,
                  image_id, user_data=True, cloud_init=True)

    mock = MagicMock(side_effect=[True, False])
    with patch.dict(boto_lc.__salt__,
                    {'boto_asg.launch_configuration_exists': mock}):
        comt = ('Launch configuration present.')
        ret.update({'comment': comt})
        assert boto_lc.present(name, image_id) == ret

        with patch.dict(boto_lc.__opts__, {'test': True}):
            comt = ('Launch configuration set to be created.')
            ret.update({'comment': comt, 'result': None})
            assert boto_lc.present(name, image_id) == ret

# 'absent' function tests: 1

def test_absent():
    '''
    Test to ensure the named launch configuration is deleted.
    '''
    name = 'mylc'

    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': ''}

    mock = MagicMock(side_effect=[False, True])
    with patch.dict(boto_lc.__salt__,
                    {'boto_asg.launch_configuration_exists': mock}):
        comt = ('Launch configuration does not exist.')
        ret.update({'comment': comt})
        assert boto_lc.absent(name) == ret

        with patch.dict(boto_lc.__opts__, {'test': True}):
            comt = ('Launch configuration set to be deleted.')
            ret.update({'comment': comt, 'result': None})
            assert boto_lc.absent(name) == ret
