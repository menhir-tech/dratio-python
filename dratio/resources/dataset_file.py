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
"""
This module contains the File class used to represent a file in the database.
"""
import warnings
from typing import TYPE_CHECKING, Union

import pandas as pd
import requests

from ..exceptions import ObjectNotFound
from .base import DatabaseResource

# Import client Type for type checking
if TYPE_CHECKING:
    from ..client import Client

    try:  # Geopandas is optional
        import geopandas as gpd
    except ImportError:
        pass


class File(DatabaseResource):
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

    _URL = "file/"

    def __init__(self, code: str, client: "Client", **kwargs):
        """
        Initializes the object with the provided code and client instance.

        Parameters
        ----------
        code : str
            Unique identifier of the File in the database.
        client: Client
            Authenticated client object used to perform requests to the database.
        **kwargs
            Additional keyword arguments used to initialize the metadata information.

        Notes
        -----
        This method does not perform any request to the database. The metadata
        information is initialized after is required.
        """
        super().__init__(code, client, **kwargs)
        self._url = None

    @property
    def url(self) -> str:
        """URL used to download the file (`str`, read-only).

        Notes
        -----
        Each time this method is called, a new access url is requested to download
        the file. The URLs are only valid for a short period of time. If you need
        to download the same data file at different times, you must request a
        new url by calling this method.

        """
        relative_url = f"{self._URL}/{self.code}/download/"
        response = self._client._perform_request(relative_url)
        response = response.json()

        url = response["url"]
        preview = response["preview"]

        # Warn about preview downloaded
        if preview:
            warnings.warn(
                "This file is not available in your plan. "
                "You are downloading a preview of the file with a few example rows. "
                "To download the full file, please change your plan or contact us at "
                "https://dratio.io/contact."
            )

        return url

    @property
    def filetype(self) -> Union[str, None]:
        """Filetype of the file (e.g. parquet, geoparquet, etc) (`str`, read-only)."""
        return self.metadata.get("filetype")

    @property
    def size(self) -> Union[int, None]:
        """Size of the file in bytes (`int`, read-only)."""
        return self.metadata.get("size")

    @property
    def start_time(self) -> Union[str, None]:
        """Start time of the file (`str`, read-only)."""
        return self.metadata.get("start_time")

    @property
    def end_time(self) -> Union[str, None]:
        """End time of the file (`str`, read-only)."""
        return self.metadata.get("end_time")

    @property
    def updated_at(self) -> Union[str, None]:
        """Date when the file was last updated (`str`, read-only)."""
        return self.metadata.get("updated_at")

    @property
    def version(self) -> Union[str, None]:
        """Version of the file (`str`, read-only)."""
        value = self.metadata.get("version")
        if value is None:
            return None
        return self._client._get_dataset_version(code=value)

    @property
    def dataset(self) -> Union[str, None]:
        """Dataset of the file (`str`, read-only)."""
        v = self.version
        if v is None:
            return None
        return v.dataset

    def to_pandas(self) -> "pd.DataFrame":
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
        # files = self.version.get_files(filetype="parquet")

        # if not files:
        #     raise ObjectNotFound("There are no available files for this dataset")

        # df_list = []
        # for file in files:
        #     url = file.url
        #     df = pd.read_parquet(url)
        #     df_list.append(df)

        # if len(df_list) > 1:
        #     df = pd.concat(df_list)

        url = self.url
        df = pd.read_parquet(url)

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

        # Dependencies used only in this method
        import io

        try:
            import geopandas as gpd

        except ImportError:
            raise ImportError(
                "geopandas is required to load a dataset with geometries."
                "You can install it using `pip install dratio[geo]` or directly using "
                "`pip install geopandas`."
            )

        # files = self.version.get_files(filetype="geoparquet")

        # if not files:
        #     raise ObjectNotFound(
        #         "There are no available files with geometries for this dataset. "
        #         "Possibly this dataset does not have any geospatial information."
        #     )

        # gdf_list = []
        # for file in files:
        #     url = file.url
        #     r = requests.get(url, allow_redirects=True)
        #     f = io.BytesIO(r.content)
        #     gdf = gpd.read_parquet(f)
        #     gdf_list.append(gdf)

        # if len(gdf_list) > 1:
        #     gdf = pd.concat(gdf_list)

        if self.metadata["filetype"] != "geoparquet":
            raise ObjectNotFound(
                "This dataset does not have any geospatial information."
                "Please, use the `to_pandas` method to download the dataset."
            )

        url = self.url
        r = requests.get(url, allow_redirects=True)
        f = io.BytesIO(r.content)
        gdf = gpd.read_parquet(f)

        return gdf
