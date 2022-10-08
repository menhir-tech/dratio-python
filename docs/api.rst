API Documentation
=================

.. rubric:: Client

The main class for interacting with the services is :class:`Client <dratio.Client>`. 
From it you can request information from Datasets and generate 
the rest of the objects of the package.

.. autosummary::
    :toctree: _api

    dratio.Client


.. rubric:: Base classes

All the elements of the database are represented as a class, 
to allow access to the information in a transparent way.

.. autosummary::
    :toctree: _api

    dratio.base.Dataset
    dratio.base.Feature
    dratio.base.Version
    dratio.base.File

.. rubric:: Exceptions

All exceptions raised by interacting with the services are subclasses
of :class:`DratioException <dratio.exceptions.DratioException>`.

.. autosummary::
    :toctree: _api

    dratio.exceptions.DratioException
    dratio.exceptions.ObjectNotFound