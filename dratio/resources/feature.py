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
This module contains the Feature class.
"""
from typing import TYPE_CHECKING, Dict, Union

from ..utils import _remove_and_copy
from .base import DatabaseResource

if TYPE_CHECKING:  # Pandas only as as type hint
    from .dataset import Dataset
    from .publisher import Publisher

__all__ = ["Feature"]


class Feature(DatabaseResource):
    """Feature of a dataset in the database

    Parameters
    ----------
    code : str
       Unique identifier of the feature in the database.
    client: Client
        Client object used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information
        (for internal usage).

    Examples
    --------

    Initialize a client object and get a dataset object

    >>> from dratio import Client
    >>> client = Client("You API key")

    Obtain the feature by its code

    >>> feature = client.get_feature("municipalities__municipality-id")
    >>> feature
    Feature('municipalities__municipality-id')

    Or obtain it from the dataset features dictionary by column name

    >>> dataset = client.get("municipalities")
    >>> feature = dataset.features.get("municipality_id")
    >>> feature
    Feature('municipalities__municipality-id')

    Get feature's attributes

    >>> feature.name
    'Municipality ID'
    >>> feature.description
    'Municipality code (int format) assigned by the National Statistics Institute...'

    Obtain all metadata associated with the feature

    >>> feature.metadata
    {'code': 'municipalities__municipality-id', ...}

    """

    _URL = "feature/"
    _LIST_FIELDS = [
        "code",
        "name",
        "column",
        "dataset_code",
        "dataset_name",
        "publisher_code",
        "publisher_name",
        "n_values",
        "granularity",
        "last_update",
        "start_data",
        "last_data",
        "scope_code",
        "scope_name",
        "level_code",
        "level_name",
        "categories",
    ]

    @property
    def name(self) -> str:
        """The name of the feature. (`str`, read-only)."""
        return self.metadata.get("name")

    @property
    def description(self) -> Union[str, None]:
        """A brief description of the feature (`str`, read-only)."""
        return self.metadata.get("description")

    @property
    def column(self) -> Union[str, None]:
        """The column name representing the feature in the dataset (`str`, read-only)."""
        return self.metadata.get("column")

    @property
    def feature_type(self) -> Union[str, None]:
        """The type of the feature (e.g., 'identifier', 'numeric') (`str`, read-only)."""
        return self.metadata.get("feature_type")

    @property
    def data_type(self) -> Union[str, None]:
        """The data type of the feature (e.g., str, float) (`str`, read-only)."""
        return self.metadata.get("data_type")

    @property
    def last_update(self) -> Union[str, None]:
        """Date of the last update of the feature (`str`, read-only)."""
        return self.metadata.get("last_update")

    @property
    def next_update(self) -> Union[str, None]:
        """Date of the next update of the feature (`str`, read-only)."""
        return self.metadata.get("next_update")

    @property
    def update_frequency(self) -> Union[str, None]:
        """Frequency of the updates of the feature (`str`, read-only)."""
        return self.metadata.get("update_frequency")

    @property
    def dataset(self) -> Union["Dataset", None]:
        """Dataset to which the feature belongs (`Dataset`, read-only)."""

        dataset_code = self.metadata.get("dataset_code")
        if dataset_code is None:
            return None

        return self._client.get_dataset(dataset_code)

    @property
    def start_data(self) -> Union[str, None]:
        """Date of the first observation of the feature (`str`, read-only)."""
        return self.metadata.get("start_data")

    @property
    def last_data(self) -> Union[str, None]:
        """Date of the last observation of the feature (`str`, read-only)."""
        return self.metadata.get("last_data")

    @property
    def scope(self) -> Union[Dict[str, str], None]:
        """Scope of the feature (`dict`, read-only)."""
        return _remove_and_copy(self.metadata.get("scope"), "icon")

    @property
    def level(self) -> Union[Dict[str, str], None]:
        """Level of the feature (`dict`, read-only)."""
        return _remove_and_copy(self.metadata.get("level"), "icon")

    @property
    def publisher(self) -> Union["Publisher", None]:
        """Publisher to which the feature belongs (`Publisher`, read-only)."""
        value = self.metadata.get("publisher")
        if value is None or value.get("code") is None:
            return None

        return self._client.get_publisher(value["code"])
