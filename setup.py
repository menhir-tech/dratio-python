from setuptools import setup


requirements = ["requests>=2.20.0,<3.0"]

with open("README.md") as f:
    readme = f.read()


setup(
    name="dratio",
    version="0.0.0",
    description="Python client library for dratio.io API Web services",
    long_description=readme,
    long_description_content_type="text/markdown",
    scripts=[],
    url="https://github.com/dratio-io/dratio-python",
    packages=["dratio"],
    license="Apache 2.0",
    platforms="Posix; MacOS X; Windows",
    setup_requires=requirements,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
    ],
    python_requires='>=3.5'
)
