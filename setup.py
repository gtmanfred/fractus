#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='fractus',
      version='0.0.1',
      description='Cloud automation using SaltStack',
      author='Daniel Wallace',
      author_email='daniel@saltstack.com',
      url='https://github.com/gtmanfred/fractus.git',
      packages=find_packages(),
      entry_points='''
        [console_scripts]
        fractus = fractus.main:main
        [salt.loader]
        utils_dirs = fractus:utils_dirs
        module_dirs = fractus:module_dirs
        state_dirs = fractus:state_dirs
        runner_dirs = fractus:module_dirs
      ''')
