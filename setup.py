#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import setuptools


if __name__ == '__main__':
    version='0.1'
    setuptools.setup(
        name='TracWikiBlog',
        version=version,
        
        description='Simple Trac Blog based on Wiki Pages',
        author='Felix Schwarz',
        author_email='felix.schwarz@oss.schwarz.eu',
        url='http://www.schwarz.eu/opensource/projects/trac_wiki_blog',
        download_url='http://www.schwarz.eu/opensource/projects/trac_wiki_blog/download/%s' % version,
        license='MIT',
        install_requires=['Trac >= 0.11', 'TracTags>=0.6'],
        
        tests_require=['nose', 'BeautifulSoup'],
        test_suite = 'nose.collector',
        
        # uses simple_super
        zip_safe=False,
        packages=setuptools.find_packages(exclude=['tests']),
        include_package_data=True,
        classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Framework :: Trac',
        ],
        entry_points = {
            'trac.plugins': [
                'trac_wiki_blog = trac_wiki_blog',
            ]
        }
    ),


