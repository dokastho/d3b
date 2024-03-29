"""
Schema site python package configuration.
"""

from setuptools import setup

setup(
    name='schemaserver',
    version='0.1.0',
    packages=['schemaserver'],
    author="Thomas Dokas",
    author_email="dokastho@umich.edu",
    url="https://github.com/dokastho/d3b",
    description="A schema maintenance server for webserver db's.",
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'arrow',
        'bs4',
        'flask',
        'html5validator',
        'pycodestyle',
        'pydocstyle',
        'pylint',
        'pytest',
        'requests',
        'selenium',
    ],
    python_requires='>=3.6'
)
