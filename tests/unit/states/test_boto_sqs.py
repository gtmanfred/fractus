# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Jayesh Kariya <jayeshk@saltstack.com>`
'''
# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import textwrap

# Import Fractus Libs
import fractus.cloudstates.boto_sqs as boto_sqs

# Import Testing Libs
import pytest
from mock import MagicMock, patch


def setup_module():
    pytest.helpers.setup_loader({
        boto_sqs: {
            '__utils__': pytest.utils,
        }
    })

# 'present' function tests: 1

def test_present():
    '''
    Test to ensure the SQS queue exists.
    '''
    name = 'mysqs'
    attributes = {'DelaySeconds': 20}
    base_ret = {'name': name, 'changes': {}}

    mock = MagicMock(
        side_effect=[{'result': b} for b in [False, False, True, True]],
    )
    mock_bool = MagicMock(return_value={'error': 'create error'})
    mock_attr = MagicMock(return_value={'result': {}})
    with patch.dict(boto_sqs.__salt__,
                    {'boto_sqs.exists': mock,
                     'boto_sqs.create': mock_bool,
                     'boto_sqs.get_attributes': mock_attr}):
        with patch.dict(boto_sqs.__opts__, {'test': False}):
            comt = ['Failed to create SQS queue {0}: create error'.format(
                name,
            )]
            ret = base_ret.copy()
            ret.update({'result': False, 'comment': comt})
            assert boto_sqs.present(name) == ret

        with patch.dict(boto_sqs.__opts__, {'test': True}):
            comt = ['SQS queue {0} is set to be created.'.format(name)]
            ret = base_ret.copy()
            ret.update({
                'result': None,
                'comment': comt,
                'pchanges': {'old': None, 'new': 'mysqs'},
            })
            assert boto_sqs.present(name) == ret
            diff = textwrap.dedent('''\
                ---
                +++
                @@ -1 +1 @@
                -{}
                +DelaySeconds: 20

            ''').splitlines()
            # Difflib adds a trailing space after the +++/--- lines,
            # programatically add them back here. Having them in the test
            # file itself is not feasible since a few popular plugins for
            # vim will remove trailing whitespace.
            for idx in (0, 1):
                diff[idx] += ' '
            diff = '\n'.join(diff)

            comt = [
                'SQS queue mysqs present.',
                'Attribute(s) DelaySeconds set to be updated:\n{0}'.format(
                    diff,
                ),
            ]
            ret.update({
                'comment': comt,
                'pchanges': {'attributes': {'diff': diff}},
            })
            assert boto_sqs.present(name, attributes) == ret

        comt = ['SQS queue mysqs present.']
        ret = base_ret.copy()
        ret.update({'result': True, 'comment': comt})
        assert boto_sqs.present(name) == ret

# 'absent' function tests: 1

def test_absent():
    '''
    Test to ensure the named sqs queue is deleted.
    '''
    name = 'test.example.com.'
    base_ret = {'name': name, 'changes': {}}

    mock = MagicMock(side_effect=[{'result': False}, {'result': True}])
    with patch.dict(boto_sqs.__salt__,
                    {'boto_sqs.exists': mock}):
        comt = ('SQS queue {0} does not exist in None.'.format(name))
        ret = base_ret.copy()
        ret.update({'result': True, 'comment': comt})
        assert boto_sqs.absent(name) == ret

        with patch.dict(boto_sqs.__opts__, {'test': True}):
            comt = ('SQS queue {0} is set to be removed.'.format(name))
            ret = base_ret.copy()
            ret.update({
                'result': None,
                'comment': comt,
                'pchanges': {'old': name, 'new': None},
            })
            assert boto_sqs.absent(name) == ret
