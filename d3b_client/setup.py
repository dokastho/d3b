"""
Replica Database python webserver client interface package configuration.
"""

from setuptools import setup

setup(
    name='d3b_client',
    version='0.1.0',
    packages=['d3b_client'],
    author="Thomas Dokas",
    author_email="dokastho@umich.edu",
    url="https://github.com/dokastho/d3b",
    description="An Authentication server for web based API's.",
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
    ],
    python_requires='>=3.6'
)
