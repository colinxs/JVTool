from setuptools import setup

setup(
    name='jvtool',
    version='1.0b',
    author='Colin Summers',
    author_email='colinxs@uw.edu',
    description='A program used process and characterize JV curve data',

    packages=['jvtool.src', 'jvtool'],

    install_requires=[
    'numpy>=1.9.2',
    'matplotlib>=1.4.3',
    'scipy>=0.15.1',
    ],

    entry_points={
        'console_scripts': [
            'jvtool = jvtool.__main__:main'
        ]
    },
)
