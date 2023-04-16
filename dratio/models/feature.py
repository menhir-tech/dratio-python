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
This module contains the Feature class.
"""
from typing import TYPE_CHECKING, Dict, Union, Any


try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from .base import DatabaseResource
from .mixins import NameDescriptionMixin, CategoryMixin

if TYPE_CHECKING:  # Pandas only as as type hint
    from .dataset import Dataset
    from .publisher import Publisher
    from .license import License


DATA_TYPES = {
    'str': 'String',
    'int': 'Integer',
    'float': 'Float',
    'text': 'Text',
    'interval': 'Interval',
    'date': 'Date',
    'datetime': 'Datetime',
    'geo': 'Geometry',
}

FEATURE_TYPES = {
    'cat': 'Category',
    'geo': 'Geometry',
    'stat': 'Statistic',
    'inter': 'Interval',
    'id': 'Identifier',
    'number': 'Number',
    'perc': 'Percentage',
}


__all__ = ["Feature"]


class Feature(DatabaseResource, NameDescriptionMixin, CategoryMixin):
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
    _EDITABLE_FIELDS = [
        "code",
        "name",
        "column",
        "description",
        "publisher",
        "dataset",
        "n_values",
        "feature_type",
        "data_type",
        "license",
        "name_es",
        "description_es",
        "reference_feature",
    ]

    @property
    def column(self) -> Union[str, None]:
        """The column name representing the feature in the dataset (`str`, read-only)."""
        return self.metadata.get("column")

    @property
    def feature_type(self) -> Union[Literal['Category', 'Geometry', 'Statistic', 'Interval', 'Identifier', 'Number', 'Percentage'],  None]:
        """The type of the feature (e.g., 'Category', 'Identifier') (`str`, read-only)."""

        raw_feature_type = self.metadata.get("feature_type")
        if raw_feature_type:
            return FEATURE_TYPES.get(raw_feature_type)

    @property
    def data_type(self) -> Union[Literal['String', 'Integer', 'Float', 'Text', 'Interval', 'Date', 'Datetime', 'Geometry'],  None]:
        """The data type of the feature (e.g., String, Integer, Float) (`str`, read-only)."""
        raw_data_type = self.metadata.get("data_type")
        if raw_data_type:
            return DATA_TYPES.get(raw_data_type)

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
        return self._client.get(code=self.metadata.get("dataset"), kind="dataset")

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
        return self._client.get(code=self.metadata.get("scope"), kind="scope")

    @property
    def data_level(self) -> Union[Dict[str, str], None]:
        """Level of the feature (`dict`, read-only)."""
        return self._client.get(code=self.metadata.get("level"), kind="data-level")

    @property
    def publisher(self) -> Union["Publisher", None]:
        """Publisher to which the feature belongs (`Publisher`, read-only)."""
        return self._client.get(code=self.metadata.get("publisher"), kind="publisher")

    @property
    def license(self) -> Union["License", None]:
        """License to which the feature belongs (`License`, read-only)."""
        license_code = self.metadata.get("license")
        dataset_license_code = self.metadata.get("dataset_license")
        license_code = license_code or dataset_license_code
        return self._client.get(code=license_code, kind="license")

    @property
    def reference_feature(self) -> Union["Feature", None]:
        """Feature to which the feature belongs (`Feature`, read-only)."""
        return self._client.get(code=self.metadata.get("reference_feature"), kind="feature")

    @property
    def reference(self) -> Union["Dataset", None]:
        """Dataset to which the feature belongs (`Dataset`, read-only)."""
        return self._client.get(code=self.metadata.get("reference"), kind="dataset")

    def _check_value(self, key: str, value: Any) -> None:
        """
        Checks if the value is valid for the given key.
        """
        super()._check_value(key, value)

        if key == 'feature_type':
            if value and value not in FEATURE_TYPES.keys():
                raise ValueError(
                    f"Invalid feature_type: {value}. Valid values are: {list(FEATURE_TYPES.keys())}")

        elif key == 'data_type':
            if value and value not in DATA_TYPES.keys():
                raise ValueError(
                    f"Invalid data_type: {value}. Valid values are: {list(DATA_TYPES.keys())}")
