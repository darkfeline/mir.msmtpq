#!/usr/bin/env python3

from setuptools import setup

setup(
    name='mir.msmtpq',
    version='1.0.0',
    description='Message queue for msmtp',
    long_description='',
    keywords='',
    url='https://github.com/darkfeline/mir.msmtpq',
    author='Allen Li',
    author_email='darkfeline@felesatra.moe',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
    ],

    packages=['mir.msmtpq'],
    entry_points={
        'console_scripts': [
            'msmtpq = mir.msmtpq.__main__:main',
        ],
    },
)
