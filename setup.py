from setuptools import setup, find_packages

# python3 setup.py bdist_wheel sdist

setup(
    name="licenseware-logblocks",
    version="0.0.1",
    url="https://github.com/licenseware/licenseware-logblocks",
    author="Licenseware",
    author_email="contact@licenseware.com",
    description="Post formated log message to slack",
    packages=find_packages(),
)
