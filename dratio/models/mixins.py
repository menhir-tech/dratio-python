#
# Copyright 2023 dratio.io. All rights reserved.
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
"""
This module contains abstract classes to be used as mixins in the
models.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Union

if TYPE_CHECKING:
    import pandas as pd
    from .feature import Feature
    from .dataset import Dataset
    from .publisher import Publisher
    from .tags import Category


class ListFeaturesMixin:
    """
    Mixin to add the list_dataset method to a model.
    """

    def list_features(
        self, format: Literal["pandas", "json", "api"] = "pandas"
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Feature"]]:
        """Returns the features associated to the object.

        Arguments
        ---------
        format : str, optional
            Format of the output. Either "pandas", "json" or "api". Defaults to "pandas".
            If "pandas", the output is a pandas DataFrame. If "json", the output is a
            list of dictionaries. If "api", the output is a list of Feature objects.

        Returns
        -------
        Union["pd.DataFrame", List[Dict[str, Any]], List["Feature"]]
            List of features associated to the object.

        Examples
        --------

        List all features available in the database:

        >>> from dratio import Client
        >>> client = Client("Your API key")
        >>> client.list_features()

        List all features associated to the publisher "ine" 
        (National Institute of Statistics):

        >>> publisher = client.get_publisher("ine")
        >>> publisher.list_features()

        List all features of a dataset (its columns):


        >>> dataset = client.get_dataset("municipalities")
        >>> dataset.list_features()


        List all features availabe at census level:


        >>> level = client.get("census", kind="data-level")
        >>> level.list_features()


        Raises
        ------
        ValueError
            If the format is not "pandas", "json" or "api".
        HTTPError
            If the request to the API fails.
        DratioException:
            If the response from the API is not valid (e.g an invalid api key
            or insufficient permissions).

        """
        filters = {self._FILTER_KEYWORD: self.code}

        return self._client.list_features(format=format, **filters)


class ListDatasetsMixin:
    """
    Mixin to add the list_dataset method to a model.
    """

    def list_datasets(
        self, format: Literal["pandas", "json", "api"] = "pandas"
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Dataset"]]:
        """Returns the datasets associated to the object.

        Arguments
        ---------
        format : str, optional
            Format of the output. Either "pandas", "json" or "api". Defaults to "pandas".
            If "pandas", the output is a pandas DataFrame. If "json", the output is a
            list of dictionaries. If "api", the output is a list of Feature objects.

        Returns
        -------
        Union["pd.DataFrame", List[Dict[str, Any]], List["Dataset"]]
            List of datasets associated to the object.

        Examples
        --------

        List all datasets available in the database:

        >>> from dratio import Client
        >>> client = Client("Your API key")
        >>> client.list_datasets()

        List all datasets associated to the publisher "ine" 
        (National Institute of Statistics):

        >>> publisher = client.get_publisher("ine")
        >>> publisher.list_datasets()


        List all features availabe at census level:


        >>> level = client.get("census", kind="data-level")
        >>> level.list_features()


        List all datasets of the category "employment":

        >>> category = client.get("employment", kind="category")
        >>> category.list_datasets()


        Raises
        ------
        ValueError
            If the format is not "pandas", "json" or "api".
        HTTPError
            If the request to the API fails.
        DratioException:
            If the response from the API is not valid (e.g an invalid api key
            or insufficient permissions).

        """
        filters = {self._FILTER_KEYWORD: self.code}

        return self._client.list_datasets(format=format, **filters)


class ListPublisherMixin:
    """
    Mixin to add the list_publishers method to a model.
    """

    def list_publishers(
        self, format: Literal["pandas", "json", "api"] = "pandas"
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Publisher"]]:
        """Returns the publishers associated to the object.

        Arguments
        ---------
        format : str, optional
            Format of the output. Either "pandas", "json" or "api". Defaults to "pandas".
            If "pandas", the output is a pandas DataFrame. If "json", the output is a
            list of dictionaries. If "api", the output is a list of Feature objects.

        Returns
        -------
        Union["pd.DataFrame", List[Dict[str, Any]], List["Publisher"]]
            List of publishers associated to the object.

        Examples
        --------

        List all publishers available in the database:

        >>> from dratio import Client
        >>> client = Client("Your API key")
        >>> client.list_publishers()

        List all publisher with the same publisher type as the publisher "ine":

        >>> publisher = client.get_publisher("ine")
        >>> publisher.publisher_type.list_publishers()



        Raises
        ------
        ValueError
            If the format is not "pandas", "json" or "api".
        HTTPError
            If the request to the API fails.
        DratioException:
            If the response from the API is not valid (e.g an invalid api key
            or insufficient permissions).

        """
        filters = {self._FILTER_KEYWORD: self.code}

        return self._client.list_publishers(format=format, **filters)


class CategoryMixin:
    """
    Mixin for models that have a categories.
    """
    @property
    def categories(self) -> List["Category"]:
        """Returns the categories associated to the object."""
        cat = self.metadata.get("categories", [])
        return [self._client.get(code=c, kind="category") for c in cat]


class NameDescriptionMixin:
    """
    Mixin for models that have a name and a description.
    """

    @property
    def name(self) -> str:
        """Returns the name of the object."""
        return self.metadata.get("name", "")

    @property
    def description(self) -> str:
        """Returns the description of the object."""
        return self.metadata.get("description", "")

