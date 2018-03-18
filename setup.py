#!usr/bin/env python

from setuptools import setup


setup(
    name='chartparser',
    version='0.2.0',
    author='Kathryn Egan',
    packages=['chartparser'],
    scripts=['bin/run.py'],
    package_data={'chartparser': [
        'data/sample_grammar.txt',
        'data/sample_lexicon.txt']},
    description='Chart parser with GUI',
    long_description=open('README.md').read(),
    install_requires=['pytest'],
    license='LICENSE.txt',
)
