API Documentation
=================

.. rubric:: Client

The main class for interacting with the services is :class:`Client <dratio.Client>`. 
From it you can request information from Datasets and generate 
the rest of the objects of the package.

.. currentmodule:: dratio

.. autosummary::
    :toctree: _autosummary

    Client


.. rubric:: Base classes

All the elements of the database are represented as a class, 
to allow access to the information in a transparent way.

.. currentmodule:: dratio.base

.. autosummary::
    :toctree: _autosummary

    Dataset
    Feature
    Version
    File

.. rubric:: Exceptions

All exceptions raised by interacting with the services are subclasses
of :class:`DratioException <dratio.exceptions.DratioException>`.

.. currentmodule:: dratio.exceptions

.. autosummary::
    :toctree: _autosummary

    DratioException
    ObjectNotFound