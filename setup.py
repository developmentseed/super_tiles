#!/usr/bin/env python
from setuptools import setup, find_packages
from imp import load_source
from os import path as op
import io

__version__ = load_source("version", "version.py").__version__

here = op.abspath(op.dirname(__file__))

# get the dependencies and installs
with io.open(op.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]
dependency_links = [x.strip().replace("git+", "") for x in all_reqs if "git+" not in x]

setup(
    name="super_tiles",
    author="Rub21",
    author_email="ruben@developmentseed",
    version=__version__,
    description="Script to generate super tiles",
    url="https://github.com/developmentseed/super_tiles",
    keywords="",
    entry_points={
        "console_scripts": [
            "super_tiles = super_tiles.main:main",
        ]
    },
    packages=find_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
)
