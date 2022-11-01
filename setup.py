from setuptools import setup


requirements = ["requests", "pandas>=0.21.1", "pyarrow", "typing_extensions"]
geo_requirements = ["geopandas>=0.8"]

with open("README.md") as f:
    readme = f.read()


setup(
    name="dratio",
    version="0.0.9",
    description="Python client library for dratio.io API Web services",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="dratio.io",
    author_email="info@dratio.io",
    scripts=[],
    project_urls={
        'Home': 'https://dratio.io',
        'GitHub': 'https://github.com/dratio-io/dratio-python',
        'Docs': 'https://dratio.readthedocs.io/',
    },
    packages=["dratio"],
    license="Apache 2.0",
    platforms="Posix; MacOS X; Windows",
    install_requires=requirements,
    extras_require={
        'geo':  geo_requirements
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
    ],
    python_requires='>=3.7',
)
