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
This module contains the dataset class.
"""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from warnings import warn

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from ..exceptions import ObjectNotFound
from .base import DatabaseResource
from .dataset_version import Version
from .mixins import CategoryMixin, ListFeaturesMixin, NameDescriptionMixin

if TYPE_CHECKING:
    from pathlib import Path

    import geopandas as gpd
    import pandas as pd

    from .dataset_file import File
    from .feature import Feature
    from .license import License
    from .publisher import Publisher
    from .tags import DataLevel, Scope


GRANULARITY_TYPES = {
    "without": "Without periodicity",
    "custom": "Custom",
    "quinquennial": "Quinquennial (Every 5 years)",
    "quadrennial": "Quadrennial (Every 4 years)",
    "triennial": "Triennial (every 3 years)",
    "biennial": "Biennial (every 2 years)",
    "annual": "Annual",
    "semiannual": "Semiannual (every 6 months)",
    "4monthly": "Every four months",
    "quarterly": "Quarterly (every 3 months)",
    "every2months": "Every two months",
    "Monthly": "Monthly",
    "twicemonthly": "Twice a month",
    "weekly": "Weekly",
    "daily": "Daily",
    "dailybusiness": "Daily Businness",
    "hourly": "Every hour",
    "everyminute": "Every minute",
}

__all__ = ["Dataset"]


class Dataset(DatabaseResource, CategoryMixin, NameDescriptionMixin, ListFeaturesMixin):
    """Representation of a dataset in the database.
    This class allows to obtain information about the dataset and its
    versions and download as a pandas or geopandas dataframe.

    Parameters
    ----------
    code : str
       Unique identifier of the feature in the database.
    version: str | None
        Version of the dataset to be used. If None, the latest version is used.
    client: Client
        Client object used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information.


    Examples
    --------
    Retrieve a dataset from the dratio.io marketplace:

    >>> from dratio import Client
    >>> client = Client('YOUR_API_KEY')
    >>> dataset = client.get('municipalities')
    >>> dataset
    Dataset('municipalities')

    Access fields included in the metadata of the dataset:

    >>> dataset.name
    'Municipalities'
    >>> dataset.description
    'Municipalities of Spain according to the name under which they are registered ...'

    Get a dictionary with all metadata:

    >>> dataset.metadata
    {'code': 'municipalities', 'name': 'Municipalities', 'description': ...}


    Get current version of the dataset

    >>> dataset.version
    Version('municipalities-v1')

    Download a dataset as a pandas dataframe:

    >>> df = dataset.to_pandas()

    Download as a geopandas dataframe (for geospatial datasets):

    >>> gdf = dataset.to_geopandas()
    """

    # URL used to perform requests to the database
    _URL = "dataset/"
    _FILTER_KEYWORD = "dataset"

    # Fields to be included in the list of datasets as a pandas dataframe
    _LIST_FIELDS = [
        "code",
        "name",
        "dataset_type",
        "last_update",
        "n_values",
        "start_data",
        "last_data",
        "granularity",
        "scope_code",
        "scope_name",
        "level_code",
        "level_name",
        "publisher_code",
        "publisher_name",
        "categories",
    ]

    _EDITABLE_FIELDS = [
        "code",
        "name",
        "name_es",
        "is_public",
        "description",
        "description_es",
        "order",
        "last_update",
        "preview",
        "timestamp_column",
        "start_data",
        "last_data",
        "n_time_slices",
        "n_values",
        "n_variables",
        "n_features",
        "next_update",
        "update_frequency",
        "granularity",
        "categories",
        "level",
        "license",
        "scope",
        "publisher",
        "related_datasets",
        "dataset_documentation",
    ]

    def __init__(self, client, code: str, version: Optional[str] = None):
        """Initializes the Dataset object"""
        super().__init__(code=code, client=client)
        if version is not None:
            raise NotImplementedError("Version selection is not implemented yet")

        self._version_code = version
        self._version = None
        self._features = None

    @property
    def features(self) -> List["Feature"]:
        """Dictionary with features indexed by column name (Dict[str, Feature], read-only)."""

        if self._features is None:
            self._features = [
                self._client.get_feature(code=code)
                for code in self.metadata.get("feature_set")
            ]

        return self._features

    @property
    def columns(self) -> List[str]:
        """Return a list with all the columns of the dataset (List[str], read-only)."""
        cols = [f.column for f in self.features]
        # Filter none values
        return [c for c in cols if c is not None]

    @property
    def version(self) -> "Version":
        """Return the current version of the dataset (Version, read-only)."""
        if self._version is None:
            versions = self.list_versions(format="json")

            if not len(versions):
                raise ObjectNotFound("Version", self.code)

            v = versions[-1].get("code")

            self._version = self._client.get(code=v, kind="version")

        return self._version

    @property
    def timestamp_column(self) -> Union[str, None]:
        """Name of the column used as timestamp (str, read-only)."""
        return self.metadata.get("timestamp_column")

    @property
    def start_data(self) -> Union[str, None]:
        """Start date of the dataset (str, read-only)."""
        return self.metadata.get("start_data")

    @property
    def last_data(self) -> Union[str, None]:
        """Last date of the dataset (str, read-only)."""
        return self.metadata.get("last_data")

    @property
    def n_time_slices(self) -> Union[int, None]:
        """Number of time slices in the dataset (int, read-only)."""
        return self.metadata.get("n_time_slices")

    @property
    def n_values(self) -> Union[int, None]:
        """Number of values in the dataset (int, read-only)."""
        return self.metadata.get("n_values")

    @property
    def n_variables(self) -> Union[int, None]:
        """Number of variables in the dataset (int, read-only)."""
        return self.metadata.get("n_variables")

    @property
    def n_features(self) -> Union[int, None]:
        """Number of features in the dataset (int, read-only)."""
        return self.metadata.get("n_features")

    @property
    def next_update(self) -> Union[str, None]:
        """Next scheduled update of the dataset (str, read-only)."""
        return self.metadata.get("next_update")

    @property
    def last_update(self) -> Union[str, None]:
        """Last update of the dataset (str, read-only)."""
        return self.metadata.get("last_update")

    @property
    def update_frequency(self) -> Union[str, None]:
        """Update frequency of the dataset (str, read-only)."""
        raw_update_frequency = self.metadata.get("update_frequency")
        return GRANULARITY_TYPES.get(raw_update_frequency)

    @property
    def granularity(self) -> Union[str, None]:
        """Granularity of the dataset, i.e., the time between different timestamps points (str, read-only)."""
        raw_granularity = self.metadata.get("granularity")
        return GRANULARITY_TYPES.get(raw_granularity)

    @property
    def publisher(self) -> Union["Publisher", None]:
        """Name of the publisher of the dataset (str, read-only)."""
        return self._client.get_publisher(code=self.metadata.get("publisher"))

    @property
    def license(self) -> Union["License", None]:
        """License of the dataset (str, read-only)."""
        return self._client.get(code=self.metadata.get("license"), kind="license")

    @property
    def scope(self) -> Union["Scope", None]:
        """Scope of the dataset (dict, read-only)."""
        return self._client.get(code=self.metadata.get("scope"), kind="scope")

    @property
    def level(self) -> Union["DataLevel", None]:
        """Level of the dataset (dict, read-only)."""
        return self._client.get(code=self.metadata.get("level"), kind="data-level")

    def upload_file(
        self,
        file: Union[str, "Path", "pd.DataFrame", "gpd.GeoDataFrame"],
        filetype: Optional[Literal["parquet", "geoparquet"]] = None,
        update: bool = True,
    ) -> "File":
        """Upload a file to the dataset."""
        file = self.version.upload_file(file=file, filetype=filetype, update=update)
        # Flush current version
        self._version = None

        return file

    def set_version(self, version: str) -> "Version":
        versions = self.list_versions(format="json")
        #  Filter version lists by version_name
        versions = [
            v for v in versions if v.get("name") == version or v.get("code") == version
        ]
        if not len(versions):
            raise ObjectNotFound("Version", version)
        v = versions[0].get("code")
        self._version = self._client.get(code=v, kind="version")
        return self

    def list_versions(
        self,
        format: Literal["pandas", "json", "api"] = "pandas",
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Version"]]:
        """List available versions of the dataset

        Returns
        -------
        List[Feature]
            List of features.

        Examples
        --------
        >>>

        Raises
        ------
        requests.exceptions.RequestException.
            If the request fails due to an HTTP or Conection Error.
        """
        return self._client.list(kind="version", dataset=self.code, format=format)

    def to_pandas(self) -> "pd.DataFrame":
        """Downloads the dataset as a pandas dataframe.

        Returns
        -------
        pandas.DataFrame
            Dataframe with the dataset.

        Examples
        --------
        >>>

        Raises
        ------
        requests.exceptions.RequestException.
            If the request fails due to an HTTP or Conection Error.
        """
        files = self.version.list_files(filetype="parquet", format="api")

        if not files:
            raise ObjectNotFound(
                "There are no available files convertible to pandas for this dataset."
                "Use `dataset.version.list_files()` to see the available files for this version."
            )

        # Logic to handle multiple files (e.g. when the dataset is too big to fit in a single file)
        df_list = []
        for file in files:
            df = file.to_pandas()
            df_list.append(df)

        if len(df_list) > 1:
            df = pd.concat(df_list)

        return df

    def _available_crosses(self, geometries: bool = False) -> List["Feature"]:
        """List available crosses of the dataset.

        Parameters
        ----------
        geometries : bool, optional
            Whether to include only crosses with geometries, by default False.

        Returns
        -------
        List[Feature]
            List of features.
        """

        available_crosses = [
            d for d in self.features if d.reference_feature is not None
        ]

        if geometries:
            available_crosses = [
                d for d in available_crosses if d.reference._has_geometries()
            ]

        return available_crosses

    def _has_geometries(self) -> bool:
        """Checks if the dataset has geometries.

        Returns
        -------
        bool
            True if the dataset has geometries, False otherwise.

        """
        geometric_files = self.version.list_files(filetype="geoparquet", format="api")
        return len(geometric_files) > 0

    def _select_cross(self, available_crosses: List["Feature"]):
        """Selects the best cross to use for the dataset.

        Parameters
        ----------
        available_crosses : List[Feature]
            List of available crosses.

        Returns
        -------
        Feature
            The best cross to use for the dataset.
        """
        if not len(available_crosses):
            return None
        if len(available_crosses) == 1:
            return available_crosses[0]

        cardinality = [a.reference.n_values for a in available_crosses]
        # computes the argmax of the cardinality (python pure, not numpy)
        max_cardinality = max(cardinality)
        max_cardinality_index = cardinality.index(max_cardinality)
        return available_crosses[max_cardinality_index]

    def to_geopandas(self, cross_strategy: str = "auto") -> "gpd.GeoDataFrame":
        """Downloads the dataset as a geopandas geodataframe.

        Returns
        -------
        geopandas.GeoDataFrame
            GeoDataFrame with the dataset.

        Notes
        -----
        This method requires the geopandas library to be installed.

        Raises
        ------
        ImportError.
            If the geopandas library is not installed. You can install it using `pip install dratio[geo]`.
        requests.exceptions.RequestException.
            If the request fails due to an HTTP or Conection Error.
        """
        import geopandas as gpd

        files = self.version.list_files(filetype="geoparquet", format="api")

        if not files:
            available_crosses = self._available_crosses(geometries=True)
            if not len(available_crosses) or cross_strategy != "auto":
                raise ObjectNotFound(
                    "There are no available files with geometries for this dataset. "
                    "Has this dataset been geocoded? "
                    "Use `dataset.version.list_files()` to see the available files for this version."
                )
            selected_cross = self._select_cross(available_crosses)
            self_column = selected_cross.column
            other_column = selected_cross.reference_feature.column

            df = self.to_pandas()
            gdf = selected_cross.reference.to_geopandas(
                cross_strategy="none"
            )  # Avoid recursion

            # Remove other columns of gdf
            gdf = gdf[[other_column, "geometry"]]
            gdf = df.merge(gdf, left_on=self_column, right_on=other_column, how="left")
            gdf = gpd.GeoDataFrame(gdf, geometry="geometry")
            return gdf

        gdf_list = []
        for file in files:
            gdf = file.to_geopandas()
            gdf_list.append(gdf)

        if len(gdf_list) > 1:
            gdf = pd.concat(gdf_list)

        return gdf

    def _check_value(self, key: str, value: Any) -> None:
        """
        Checks if the value is valid for the given key.
        """
        super()._check_value(key, value)

        if key == "granularity" or key == "update_frequency":
            if value and value not in GRANULARITY_TYPES.keys():
                raise ValueError(
                    f"Invalid {key}: {value}. Valid values are: {list(GRANULARITY_TYPES.keys())}"
                )

        if key == "timestamp_column":
            if value not in self.columns:
                raise ValueError(
                    f"Invalid {key}: {value}. Valid values are: {self.columns}"
                )

    def add_feature(self, feature: "Feature") -> None:
        """Adds a feature to the dataset.

        Parameters
        ----------
        feature : Feature
            Feature to add to the dataset.

        Examples
        --------
        >>>

        Raises
        ------
        requests.exceptions.RequestException.
            If the request fails due to an HTTP or Conection Error.
        """

        if feature.column is None:
            raise ValueError("The feature must have a column associated with it.")

        if self._exists:
            # Check if the feature is already in the dataset
            columns = self.columns
            codes = [f.code for f in self.features]

            if feature.code in codes:
                warn(
                    f"The feature {feature.code} is already in the dataset.\n"
                    f"Update the feature previously added instead of adding a new one.\n"
                    f"Already added features: {codes}"
                )
                return
            if feature.column in columns:
                warn(
                    f"The column {feature.column} is already in the dataset.\n"
                    f"Update the feature previously added instead of adding a new one.\n"
                    f"U"
                )
                return

        # Add the feature to the dataset
        feature["dataset"] = self

        # Case new dataset and first feature
        if self._features is None:
            self._features = []
        self._features.append(feature)

    def _save_subresources(self) -> None:
        """
        Save the feature.
        """
        super()._save_subresources()

        # Save the license items
        for feature in self.features:
            feature.save()

    def save(self) -> "Dataset":
        super().save()
        # self._features = None

    def list_files(
        self,
        filetype: Optional[Literal["parquet", "geoparquet"]] = None,
        format: Literal["pandas", "json", "api"] = "pandas",
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["File"]]:
        """Returns a list of files associated to the version.

        Parameters
        ----------
        filetype : Optional[Literal["parquet", "geoparquet"]]
            Type of file to filter. If None, all files are returned.
        format: Literal["pandas", "json"]
            Format of the returned list, either a list of dictionaries or a
            pandas DataFrame.

        Returns
        -------
        Literal["pandas", "json"]
            List of files associated to the version.
        """
        return self.version.list_files(filetype=filetype, format=format)

    def metadata_from_pandas(
        self,
        df: Union["pd.DataFrame", "gpd.GeoDataFrame"],
        publisher: Union[str, "Publisher"],
        license: Optional[Union[str, "License"]] = None,
        timestamp_column: str = "timestamp",
    ) -> "Dataset":
        """Automatically generates the metadata of the dataset from a pandas dataframe.
        This method is useful to create a dataset from a pandas dataframe, and is
        intended to be used for data providers that want to upload their data to dratio.io.

        Parameters
        ----------
        df : Union[pandas.DataFrame, geopandas.GeoDataFrame]
            Pandas dataframe with the data.
        publisher : Union[str, Publisher]
            Publisher of the dataset.
        license : Optional[Union[str, License]]
            License of the dataset.
        timestamp_column : str
            Name of the column used as timestamp (if applicable).

        Returns
        -------
        Dataset
            Dataset object with the metadata generated from the pandas dataframe.
        """
        from ..provider.provider_utils import metadata_from_pandas

        return metadata_from_pandas(
            dataset=self,
            df=df,
            publisher=publisher,
            license=license,
            timestamp_column=timestamp_column,
        )
