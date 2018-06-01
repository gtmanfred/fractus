# -*- coding: utf-8 -*-
'''
Unit tests for the boto_cloudfront state module.
'''
# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import copy
import textwrap

# Import Fractus Libs
import fractus.cloudstates.boto_cloudfront as boto_cloudfront

# Import Test Libs
import pytest
from mock import MagicMock, patch


name = 'my_distribution'
base_ret = {'name': name, 'changes': {}}

# Most attributes elided since there are so many required ones
config = {'Enabled': True, 'HttpVersion': 'http2'}
tags = {'test_tag1': 'value1'}


def setup_module():
    pytest.helpers.setup_loader({
        boto_cloudfront: {
            '__utils__': pytest.utils,
        }
    })


def base_ret_with(extra_ret):
   new_ret = copy.deepcopy(base_ret)
   new_ret.update(extra_ret)
   return new_ret


def test_present_distribution_retrieval_error():
   '''
   Test for boto_cloudfront.present when we cannot get the distribution.
   '''
   mock_get = MagicMock(return_value={'error': 'get_distribution error'})
   with patch.multiple(boto_cloudfront,
       __salt__={'boto_cloudfront.get_distribution': mock_get},
       __opts__={'test': False},
   ):
       comment = 'Error checking distribution {0}: get_distribution error'
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': False,
               'comment': comment.format(name),
           })

def test_present_from_scratch():
   mock_get = MagicMock(return_value={'result': None})

   with patch.multiple(boto_cloudfront,
       __salt__={'boto_cloudfront.get_distribution': mock_get},
       __opts__={'test': True},
   ):
       comment = 'Distribution {0} set for creation.'.format(name)
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': None,
               'comment': comment,
               'pchanges': {'old': None, 'new': name},
           })

   mock_create_failure = MagicMock(return_value={'error': 'create error'})
   with patch.multiple(boto_cloudfront,
       __salt__={
           'boto_cloudfront.get_distribution': mock_get,
           'boto_cloudfront.create_distribution': mock_create_failure,
       },
       __opts__={'test': False},
   ):
       comment = 'Error creating distribution {0}: create error'
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': False,
               'comment': comment.format(name),
           })

   mock_create_success = MagicMock(return_value={'result': True})
   with patch.multiple(boto_cloudfront,
       __salt__={
           'boto_cloudfront.get_distribution': mock_get,
           'boto_cloudfront.create_distribution': mock_create_success,
       },
       __opts__={'test': False},
   ):
       comment = 'Created distribution {0}.'
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': True,
               'comment': comment.format(name),
               'changes': {'old': None, 'new': name},
           })

def test_present_correct_state():
   mock_get = MagicMock(return_value={'result': {
       'distribution': {'DistributionConfig': config},
       'tags': tags,
       'etag': 'test etag',
   }})
   with patch.multiple(boto_cloudfront,
       __salt__={'boto_cloudfront.get_distribution': mock_get},
       __opts__={'test': False},
   ):
       comment = 'Distribution {0} has correct config.'
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': True,
               'comment': comment.format(name),
           })

def test_present_update_config_and_tags():
   mock_get = MagicMock(return_value={'result': {
       'distribution': {'DistributionConfig': {
           'Enabled': False,
           'Comment': 'to be removed',
       }},
       'tags': {'bad existing tag': 'also to be removed'},
       'etag': 'test etag',
   }})

   diff = textwrap.dedent('''\
       ---
       +++
       @@ -1,5 +1,5 @@
        config:
       -  Comment: to be removed
       -  Enabled: false
       +  Enabled: true
       +  HttpVersion: http2
        tags:
       -  bad existing tag: also to be removed
       +  test_tag1: value1

   ''').splitlines()
   # Difflib adds a trailing space after the +++/--- lines,
   # programatically add them back here. Having them in the test file
   # itself is not feasible since a few popular plugins for vim will
   # remove trailing whitespace.
   for idx in (0, 1):
       diff[idx] += ' '
   diff = '\n'.join(diff)

   with patch.multiple(boto_cloudfront,
       __salt__={'boto_cloudfront.get_distribution': mock_get},
       __opts__={'test': True},
   ):
       header = 'Distribution {0} set for new config:'.format(name)
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': None,
               'comment': '\n'.join([header, diff]),
               'pchanges': {'diff': diff},
           })

   mock_update_failure = MagicMock(return_value={'error': 'update error'})
   with patch.multiple(boto_cloudfront,
       __salt__={
           'boto_cloudfront.get_distribution': mock_get,
           'boto_cloudfront.update_distribution': mock_update_failure,
       },
       __opts__={'test': False},
   ):
       comment = 'Error updating distribution {0}: update error'
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': False,
               'comment': comment.format(name),
           })

   mock_update_success = MagicMock(return_value={'result': True})
   with patch.multiple(boto_cloudfront,
       __salt__={
           'boto_cloudfront.get_distribution': mock_get,
           'boto_cloudfront.update_distribution': mock_update_success,
       },
       __opts__={'test': False},
   ):
       assert boto_cloudfront.present(name, config, tags) == \
           base_ret_with({
               'result': True,
               'comment': 'Updated distribution {0}.'.format(name),
               'changes': {'diff': diff},
           })
