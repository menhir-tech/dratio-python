#
# Copyright 2022 dratio.io. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
#
# The use of the services offered by this client must be in accordance with
# dratio's terms and conditions. You may obtain a copy of the terms at
#
#     https://dratio.io/legal/terms/
#

import os

from setuptools import setup


def read(rel_path: str) -> str:
    """Read a file relative to the setup.py file"""
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    try:
        with open(os.path.join(here, rel_path)) as fp:
            return fp.read()
    except IOError:
        return ""


def get_version(rel_path: str) -> str:
    """Read the version number from a source file"""
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="dratio",
    version=get_version("dratio/__init__.py"),
    description="Python client library for dratio.io API Web services",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="dratio.io",
    author_email="info@dratio.io",
    scripts=[],
    project_urls={
        "Home": "https://dratio.io",
        "GitHub": "https://github.com/dratio-io/dratio-python",
        "Docs": "https://dratio.readthedocs.io/",
    },
    packages=["dratio"],
    license="Apache 2.0",
    platforms="Posix; MacOS X; Windows",
    install_requires=["requests", "pandas>=0.21.1", "pyarrow", "typing_extensions"],
    extras_require={"geo": ["geopandas>=0.8"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Sociology",
    ],
    python_requires=">=3.7",
)
