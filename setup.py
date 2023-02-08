from setuptools import setup, find_packages

# python3 setup.py bdist_wheel sdist

with open("requirements.txt", "r") as f:
    REQUIREMENTS = f.readlines()

setup(
    name="slack-webhoook-bot",
    version="0.0.1",
    url="https://github.com/licenseware/slack-webhook-bot",
    author="Licenseware",
    author_email="contact@licenseware.com",
    description="Post formated log message to slack",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
)
