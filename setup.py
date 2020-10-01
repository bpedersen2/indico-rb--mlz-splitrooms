'''
Created on Mar 9, 2018

@author: pedersen
'''
from __future__ import unicode_literals

from setuptools import find_packages, setup

setup(
    name='mlz-indico-splitrooms',
    version='2.3',
    url='https://github.com/bpedersen2/mlz-indico-splitrooms',
    license='MIT',
    author='MLZ Indico Team',
    author_email='bjoern.pedersen@frm2.tum.de',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['indico>=2.3.0'],
    entry_points={
        'indico.plugins': {'split_rooms=indico_rb_splitrooms.plugin:SplitRoomPlugin'},
    },
    classifiers=[
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
