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
"""
This module contains the Publisher class. A publisher is an data source 
from which datasets are obtained.
"""
from typing import TYPE_CHECKING, Any, Dict, List, Union

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from ..utils import _remove_and_copy
from .base import DatabaseResource

if TYPE_CHECKING:  # Pandas only as as type hint
    import pandas as pd

    from .dataset import Dataset
    from .feature import Feature

__all__ = ["Publisher"]


class Publisher(DatabaseResource):
    """
    Class to represent a publisher in the database.
    A publisher is an data source from which datasets are obtained.

    Parameters
    ----------
    code : str
        Unique identifier of the publisher in the database.

    Examples
    --------

    Get a table with all publishers in the database

    >>> from dratio import Client
    >>> client = Client("Your API key")
    >>> df_publisher = client.list_publishers()

    Get a publisher object by its code

    >>> publisher = client.get_publisher("ine")
    >>> publisher
    Publisher('ine')

    Get a table with all datasets associated to the publisher

    >>> df_datasets = publisher.list_datasets()

    Get a table with all features associated to the publisher

    >>> df_features = publisher.list_features()

    Access the publisher's metadata raw dictionary

    >>> publisher.metadata
    {'code': 'ine', 'name': 'National Statistics Institute (INE)', ...}

    """

    _URL = "publisher/"
    _LIST_FIELDS = [
        "code",
        "name",
        "url",
        "last_update",
        "n_datasets",
        "n_variables",
        "n_features",
        "start_data",
        "last_data",
        "scope_code",
        "scope_name",
        "publisher_type_code",
        "publisher_type_name",
        "categories",
    ]

    @property
    def name(self) -> str:
        """The name of the publisher (`str`, read-only)."""
        return self.metadata.get("name")

    @property
    def url(self) -> Union[str, None]:
        """The URL of the publisher's website (`str`, read-only)."""
        return self.metadata.get("url")

    @property
    def last_update(self) -> Union[str, None]:
        """The date when the publisher's information was last updated (`str`, read-only)."""
        return self.metadata.get("last_update")

    @property
    def categories(self) -> List[Dict[str, str]]:
        """The categories associated with the publisher (`str`, read-only)."""
        return self.metadata.get("categories", [])

    @property
    def n_datasets(self) -> Union[int, None]:
        """The number of datasets associated with the publisher (`int`, read-only)."""
        return self.metadata.get("n_datasets")

    @property
    def n_variables(self) -> Union[int, None]:
        """The number of variables associated with the publisher (`int`, read-only)."""
        return self.metadata.get("n_variables")

    @property
    def n_features(self) -> Union[int, None]:
        """The number of features associated with the publisher (`int`, read-only)."""
        return self.metadata.get("n_features")

    @property
    def start_data(self) -> Union[str, None]:
        """The start date of the data provided by the publisher (`str`, read-only)."""
        return self.metadata.get("start_data")

    @property
    def last_data(self) -> Union[str, None]:
        """The last date of the data provided by the publisher (`str`, read-only)."""
        return self.metadata.get("last_data")

    @property
    def scope(self) -> Union[Dict[str, str], None]:
        """The scope of the publisher (`dict`, read-only)."""

        return _remove_and_copy(self.metadata.get("scope"), "icon")

    @property
    def publisher_type(self) -> Union[Dict[str, str], None]:
        """The type of the publisher (`dict`, read-only)."""

        return _remove_and_copy(self.metadata.get("publisher_type"), "icon")

    def list_datasets(
        self, format: Literal["pandas", "json", "api"] = "pandas"
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Dataset"]]:
        """Returns a list of datasets associated to the publisher.

        Arguments
        ---------
        format : str, optional
            Format of the output. Either "pandas", "json" or "api". Defaults to "pandas".
            If "pandas", the output is a pandas DataFrame. If "json", the output is a
            list of dictionaries. If "api", the output is a list of Dataset objects.


        Returns
        -------
        Union["pd.DataFrame", List[Dict[str, Any]], List["Dataset"]]
            List of datasets associated to the publisher.
        """

        return self._client.list_datasets(publisher=self.code, format=format)

    def list_features(
        self, format: Literal["pandas", "json", "api"] = "pandas"
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Feature"]]:
        """Returns a list of features associated to the publisher.

        Arguments
        ---------
        format : str, optional
            Format of the output. Either "pandas", "json" or "api". Defaults to "pandas".
            If "pandas", the output is a pandas DataFrame. If "json", the output is a
            list of dictionaries. If "api", the output is a list of Feature objects.

        Returns
        -------
        Union["pd.DataFrame", List[Dict[str, Any]], List["Feature"]]
            List of features associated to the publisher.
        """
        return self._client.list_features(publisher=self.code, format=format)
