# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

setup(
    name="BatteryML",
    version="0.0.1",
    description="An Open-Source Tool for Machine Learning on Battery Degradation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Microsoft Corporation",
    url="https://github.com/microsoft/BatteryML",
    packages=find_packages(exclude=['scripts']),
    install_requires=required_packages,
    scripts=["bin/batteryml"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
)
