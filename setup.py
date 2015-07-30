# pylint: skip-file

from setuptools import setup, find_packages

setup(
    name='s2sproxy-module-s2sproxy_module',
    version='0.1',
    author='DIRG',
    author_email='dirg@its.umu.se',
    url='https://github.com/its-dirg/s2sproxy-module-comanage',
    packages=find_packages('src'),
    package_dir={'': 'src'}
)
