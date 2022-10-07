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
#     https://dratio.io/legal/terms
#
import io
from typing import Any, Dict, Literal, Optional

import pandas as pd
import requests

try:  # Geopandas: Optional dependency
    import geopandas as gpd
    _has_geopandas = True
except ImportError:
    _has_geopandas = False

from .exceptions import ObjectNotFound


class BaseDBObject:
    """Abstract class used to represent objects in the database.
    Encapsulates common logic for retrieving information from database objects.

    Parameters
    ----------
    code : str
       Unique identifier of the object in the database.
    client: Client
        Client object used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information.

    Attributes
    ----------
    URL : str
        Relative URL used to perform requests to the database (class attribute).

    Notes
    -----
    This class is intended for internal API use. See the `Client` and `Dataset`
    classes for more information.
    """

    def __init__(self, code: str, client, **kwargs):
        self.code = code
        self._client = client
        self._fetched = False
        self._metadata = {'code': code, **kwargs}

    def __repr__(self) -> str:
        """Returns a string representation of the object"""
        return f"{self.__class__.__name__}('{self.code}')"

    @property
    def metadata(self) -> Dict[str, Any]:
        """Information associated (metadata) to the object referenced in the database
        (`Dict[str, Any]`, read-only).

        Notes
        -----
        The first time the property is accessed, a request is made to the server to
        obtain the information. In successive accesses the previously loaded information
        is returned. In case of needing to update the information, a new object
        must be created.
        """
        if not self._fetched:
            self.fetch()

        return self._metadata

    def __getitem__(self, key: str) -> Any:
        """Getter for metadata atributes. Allows access to the object's
        information elements directly from the class.
        """
        return self.metadata[key]

    def fetch(self) -> "BaseDBObject":
        """Updates the metadata dictionary of the object.
        This method perform an HTTP request to the server to obtain the information.


        Returns
        -------
            self: BaseDBObject
                The object itself.

        Notes
        -----
        This method modifies the object's metadata attribute.


        Raises
        ------
            requests.exceptions.RequestException.
                If the request fails.
            ObjectNotFound.
                If the object is not found in the database.

        """
        relative_url = f"{self.URL}/{self.code}/"
        response = self._client._perform_request(
            relative_url, allowed_status=[404])

        if response.status_code == 404:
            raise ObjectNotFound(self.__class__.__name__, self.code)

        self._metadata = response.json()
        self._fetched = True

        return self


class Feature(BaseDBObject):
    """Feature of a dataset in the database

    Parameters
    ----------
    code : str
       Unique identifier of the feature in the database.
    client: Client
        Client object used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information.

    """
    URL = "upload/feature/"


class File(BaseDBObject):
    """File of a dataset in the database

    Parameters
    ----------
    code : str
       Unique identifier of the feature in the database.
    client: Client
        Client object used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information.

    """
    URL = "marketplace/token/file/"

    def __init__(self, code: str, client, **kwargs):
        super().__init__(code, client, **kwargs)
        self._url = None

    @property
    def url(self):
        """URL used to download the file (`str`, read-only).

        Notes
        -----
        Each time this method is called, a new access url is requested to download 
        the file. The URLs are only valid for a short period of time. If you need 
        to download the same data file at different times, you must request a 
        new url by calling this method. 

        """
        if self._url is None:
            self.fetch()
            self._url = self._metadata.get('url')

        return self._url


class Version(BaseDBObject):
    """Version of a dataset in the database

    Parameters
    ----------
    code : str
       Unique identifier of the feature in the database.
    client: Client
        Client object used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information.

    """
    URL = "marketplace/token/version/"

    def get_files(self, filetype: Optional[Literal["parquet", "geoparquet"]] = None) -> list[File]:
        """Returns a list of files associated to the version.

        Parameters
        ----------
        filetype : Optional[Literal["parquet", "geoparquet"]]
            Type of file to filter. If None, all files are returned.

        Returns
        -------
        list[File]
            List of files associated to the version.
        """
        params = dict(version=self.code)
        if filetype is not None:
            params["filetype"] = filetype

        files = self._client._perform_request(
            url=File.URL, params=params).json()

        return [File(client=self._client, **file) for file in files]


class Dataset(BaseDBObject):
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
    >>> client = Client(key='<your_api_key>')
    >>> dataset = client.get(code='unemployment-municipality')
    >>> dataset
    Dataset('unemployment-municipality')

    Access fields included in the metadata of the dataset:

    >>> dataset["description"]
    'Monthly data on the number of unemployed persons by municipality, ...'

    Get a dictionary with all metadata:

    >>> dataset.metadata
    {'code': 'unemployment-municipality', 'name': 'Unemployment, contracts and ...', ...}


    Get current version of the dataset

    >>> dataset.version
    Version('unemployment-municipality-v1')

    Download a dataset as a pandas dataframe:

    >>> df = dataset.to_pandas()
    """
    URL = "marketplace/token/datasets/"

    def __init__(self, client, code: str, version: Optional[str] = None):
        super().__init__(code=code, client=client)
        if version is not None:
            raise NotImplementedError(
                "Version selection is not implemented yet")

        self._version_code = version
        self._version = None
        self._features = None

    def _fetch_features(self) -> None:
        """Fetches information of the dataset features"""
        params = {"dataset": self.code}
        features = self._client._perform_request(
            Feature.URL, params=params)
        self._features = features.json()

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
    def features(self) -> list[Feature]:
        """Return a list with all the features of the dataset (list[Feature], read-only)."""
        if not self._fetched:
            self.fetch()
        return self._features

    @property
    def version(self) -> Version:
        """Return the current version of the dataset (Version, read-only)."""
        if self._version is None:
            v = self._client._perform_request(url=Version.URL, params=dict(
                dataset=self.code)).json()

            if len(v) != 1:
                raise ObjectNotFound("Version", self.code)

            self._version = Version(client=self._client, **v[0])

        return self._version

    def to_pandas(self):
        """Downloads the dataset as a pandas dataframe.

        Returns
        -------
        pandas.DataFrame
            Dataframe with the dataset.

        Raises
        ------
        requests.exceptions.RequestException.
            If the request fails due to an HTTP or Conection Error.
        """
        files = self.version.get_files(filetype='parquet')

        if not files:
            raise ObjectNotFound(
                "There are no available files for this dataset")

        df_list = []
        for file in files:
            url = file.url
            df = pd.read_parquet(url)
            df_list.append(df)

        if len(df_list) > 1:
            df = pd.concat(df_list)

        return df

    def to_geopandas(self):
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
        requests.exceptions.RequestException.
            If the request fails due to an HTTP or Conection Error.
        """
        if not _has_geopandas:
            raise ImportError(
                "geopandas is required to load a dataset with geometries")

        files = self.version.get_files(filetype='geoparquet')

        if not files:
            raise ObjectNotFound(
                "There are no available files with geometries for this dataset. "
                "Has this dataset been geocoded?")

        gdf_list = []
        for file in files:
            url = file.url
            r = requests.get(url, allow_redirects=True)
            f = io.BytesIO(r.content)
            gdf = gpd.read_parquet(f)
            gdf_list.append(gdf)

        if len(gdf_list) > 1:
            gdf = pd.concat(gdf_list)

        return gdf
