.. dratio documentation master file, created by
   sphinx-quickstart on Fri Oct  7 16:58:33 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: https://dratio.io/branding/logo.png
  :alt: Dratio.io: Python API client for dratio web services
  :target: https://dratio.io


Welcome to dratio's client documentation!
=========================================

.. image:: https://badge.fury.io/py/dratio.svg
  :alt: PyPI version
  :target: https://pypi.org/project/dratio/

.. image:: https://readthedocs.org/projects/dratio/badge/?version=latest
    :target: https://dratio.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/dratio
  :alt: Python Version
  :target: https://pypi.org/project/dratio/

.. image:: https://img.shields.io/github/license/dratio-io/dratio-python
  :alt: License
  :target: https://github.com/dratio-io/dratio-python/blob/main/LICENSE



.. rubric:: Data as-a-service to make better decisions based on technology

This client allows you to interact with the services offered by 
`dratio.io <https://dratio.io>`_ using Python.
You can download ready-to-use datasets for all types of industries. 
All data is reviewed, documented and linked together by common variables, allowing you 
to reference directly with your data without spending time on integration.

.. contents::

Installation
------------

Currently, dratio's client is available in Python 3.7 to 3.10, regardless of the platform. 
The stable version can be installed via `PyPI <https://pypi.org/project/dratio/>`_.

.. code-block:: bash

   pip install dratio

In case of using datasets with geographic information, you must have `geopandas <https://geopandas.org/en/stable/>`_ 
installed in your Python environment. You can also install the package with all the necessary 
dependencies directly from `PyPI <https://pypi.org/project/dratio/>`_.

.. code-block:: bash

   pip install dratio[geo]


Create API Keys
---------------
Before you can start using the services offered and access all the datasets, 
you will need to `create an API key <https://dratio.io/app/api/>`_. 
If you are not registered you can `create an account <https://dratio.io/getstarted/>`_ 
on `dratio.io`_.

.. note::
   Please, store your API Keys in a safe place and never share them publicly, 
   as they give access to all services offered on your behalf. 
   In case of a leak, you can delete and create new keys 
   from `the platform <https://dratio.io/app/api/>`_.

Get started
-----------

The :class:`Client <dratio.Client>` class allows you to access all API resources using your key.

.. code-block:: python

   from dratio import Client

   client = Client('<your_api_key>')


Basic functionalities allow you to search and filter datasets available for download.

.. code-block:: python

   client.get_datasets()

Once a :class:`Dataset <dratio.base.Dataset>` is selected, you can access its information and 
download its content as a Pandas 
:class:`DataFrame <pandas.DataFrame>` or, 
in case of datasets with geographic information, as a 
:class:`GeoDataFrame <geopandas.GeoDataFrame>`.

.. code-block:: python

   dataset = client.get('municipalities')

   df = dataset.to_pandas() # Download as DataFrame
   gdf = dataset.to_geopandas() # GeoDataFrame with geographic information


License
-------   

This source code is licensed under the Apache License, Version 2.0. You may obtain a copy of
the License at `apache.org <https://www.apache.org/licenses/LICENSE-2.0>`_.

The use of Dratio's web services must be in accordance with 
the `terms and conditions <https://dratio.io/legal/terms>`_ that can 
be found at `dratio.io/legal/ <https://dratio.io/legal/>`_.


Support
-------

This library is supported by dratio's team.
If you find a bug, or have a feature suggestion, we would appreciate it if you 
`create an issue <https://github.com/dratio-io/dratio-python>`_ or
contact us through `our page <https://dratio.io/contact/>`_ or via mail
to `info@dratio.io <mailto:info@dratio.io>`_.

.. toctree::
   :hidden:

   Welcome <self>


.. toctree::
   :maxdepth: 1
   :hidden:

   api