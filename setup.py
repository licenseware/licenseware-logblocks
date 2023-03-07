import os

from setuptools import find_packages, setup

# python3 setup.py bdist_wheel sdist

with open("README.md", "r") as fd:
    LONG_DESCRIPTION = fd.read()

PACKAGE_VERSION = os.environ["PACKAGE_VERSION"]

setup(
    name="licenseware-logblocks",
    version=PACKAGE_VERSION,
    url="https://github.com/licenseware/licenseware-logblocks",
    author="Licenseware",
    author_email="contact@licenseware.com",
    description="Post formatted log messages to slack, mentioning users when error ocurrs",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["logblocks = logblocks.logblocks:main"]},
    packages=find_packages(include=["logblocks", "logblocks.*"]),
)
