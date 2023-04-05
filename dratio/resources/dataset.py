from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import pandas as pd

from ..exceptions import ObjectNotFound
from .base import DatabaseResource
from .dataset_version import Version

if TYPE_CHECKING:
    from .publisher import Publisher
    from .feature import Feature
    import geopandas as gpd
    from ..client import Client

from ..utils import _remove_and_copy

__all__ = ["Dataset"]


class Dataset(DatabaseResource):
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

    def __init__(self, client, code: str, version: Optional[str] = None):
        """Initializes the Dataset object"""
        super().__init__(code=code, client=client)
        if version is not None:
            raise NotImplementedError("Version selection is not implemented yet")

        self._version_code = version
        self._version = None
        self._features = None

    def _fetch_features(self) -> None:
        """Fetches information of the dataset features"""
        params = {"dataset": self.code}
        url = self._client._FEATURE_CLASS._URL
        features = self._client._perform_request(url, params=params)
        features = features.json()
        self._features = {
            feature["column"]: self._client.get_feature(feature["code"])
            for feature in features
        }

    def fetch(self) -> "Dataset":
        """Updates the metadata dictionary of the dataset.

        This method perform an HTTP request to the server to obtain the information.

        Returns
        -------
            self: Dataset
                The object itself.

        Notes
        -----
        This method modifies the object's metadata attribute.


        Raises
        ------
        requests.exceptions.RequestException.
            If the request fails due to an HTTP or Conection Error..
        ObjectNotFound.
            If the object is not found in the database.

        """
        super().fetch()
        self._fetch_features()

        return self

    @property
    def features(self) -> Dict[str, "Feature"]:
        """Dictionary with features indexed by column name (Dict[str, Feature], read-only)."""
        if not self._fetched:
            self.fetch()
        return self._features

    @property
    def columns(self) -> List[str]:
        """Return a list with all the columns of the dataset (List[str], read-only)."""
        return list(self.features.keys())

    @property
    def version(self) -> Version:
        """Return the current version of the dataset (Version, read-only)."""
        if self._version is None:
            v = self._client._perform_request(
                url=Version._URL, params=dict(dataset=self.code)
            ).json()

            if len(v) != 1:
                raise ObjectNotFound("Version", self.code)

            self._version = Version(client=self._client, **v[0])

        return self._version

    @property
    def name(self) -> str:
        """Name of the dataset (str, read-only)."""
        return self.metadata["name"]

    @property
    def description(self) -> Union[str, None]:
        """Description of the dataset (str, read-only)."""
        return self.metadata.get("description")

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
        return self.metadata.get("update_frequency")

    @property
    def granularity(self) -> Union[str, None]:
        """Granularity of the dataset, i.e., the time between different timestamps points (str, read-only)."""
        return self.metadata.get("granularity")

    @property
    def publisher(self) -> Union["Publisher", None]:
        """Name of the publisher of the dataset (str, read-only)."""
        publisher_code = self.metadata.get("publisher", {}).get("code")
        return self._client.get_publisher(code=publisher_code)

    @property
    def license(self) -> Union[str, None]:
        """License of the dataset (str, read-only)."""
        return self.metadata.get("license")

    @property
    def scope(self) -> Union[Dict[str, str], None]:
        """Scope of the dataset (dict, read-only)."""
        return _remove_and_copy(self.metadata.get("scope"), "icon")

    @property
    def categories(self) -> Union[List[str], None]:
        """Categories of the dataset (List[str], read-only)."""
        return self.metadata.get("categories")

    @property
    def level(self) -> Union[Dict[str, str], None]:
        """Level of the dataset (dict, read-only)."""
        return _remove_and_copy(self.metadata.get("level"), "icon")

    def list_features(
        self,
        format: Literal["pandas", "json", "api"] = "pandas",
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Feature"]]:
        """List the features of the dataset.

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
        return self._client.list(kind="feature", dataset=self.code, format=format)

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

    def to_geopandas(self) -> "gpd.GeoDataFrame":
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

        files = self.version.list_files(filetype="geoparquet", format="api")

        if not files:
            raise ObjectNotFound(
                "There are no available files with geometries for this dataset. "
                "Has this dataset been geocoded?"
                "Use `dataset.version.list_files()` to see the available files for this version."
            )

        gdf_list = []
        for file in files:
            gdf = file.to_geopandas()
            gdf_list.append(gdf)

        if len(gdf_list) > 1:
            gdf = pd.concat(gdf_list)

        return gdf
