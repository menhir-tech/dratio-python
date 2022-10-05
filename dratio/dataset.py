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

# Geopandas: Optional dependency
try:
    import geopandas as gpd
    _has_geopandas = True
except ImportError:
    _has_geopandas = False


class BaseDBObject:
    """
    Abstract class used to represent objects in the database
    """

    def __init__(self, code: str, client, **kwargs):
        self.code = code
        self._client = client
        self._fetched = False
        self._metadata = {'code': code, **kwargs}

    def __repr__(self):
        """Represents BaseDBObject object as a string"""
        return f"{self.__class__.__name__}('{self.code}')"

    @property
    def metadata(self) -> Dict[str, Any]:
        """Returns a dictionary with all metadata associated with the object"""
        if not self._fetched:
            self.fetch()

        return self._metadata.copy()

    def __getitem__(self, key: str) -> Any:
        """Getter for metadata atributes"""
        return self.metadata[key]

    def fetch(self) -> "BaseDBObject":
        """Fetches all metadata related to an object"""
        relative_url = f"{self.URL}/{self.code}/"
        metadata = self._client._perform_request(relative_url).json()
        self._metadata = metadata
        self._fetched = True

        return self


class Feature(BaseDBObject):
    """Wrapper for the features of a dataset"""
    URL = "upload/feature/"


class File(BaseDBObject):
    """Wrapper for the features of a dataset"""
    URL = "marketplace/token/file/"

    def __init__(self, code: str, client, **kwargs):
        super().__init__(code, client, **kwargs)
        self._url = None

    @property
    def url(self):
        if self._url is None:
            self.fetch()
            self._url = self._metadata.get('url')

        return self._url


class Version(BaseDBObject):
    """Wrapper for the features of a dataset"""
    URL = "marketplace/token/version/"

    def get_files(self, filetype: Optional[Literal["parquet", "geoparquet"]] = None) -> list[File]:

        params = dict(version=self.code)
        if filetype is not None:
            params["filetype"] = filetype

        files = self._client._perform_request(
            url=File.URL, params=params).json()

        return [File(client=self._client, **file) for file in files]


class Dataset(BaseDBObject):
    """Context manager for the creation of a dataset"""
    URL = "marketplace/token/datasets/"

    def __init__(self, client, code: str, version: Optional[str] = None):

        super().__init__(code=code, client=client)
        self._version_code = version
        self._version = None
        self._features = None

    def _fetch_features(self):
        """Fetches information of the dataset features"""
        params = {"dataset": self.code}
        features = self._client._perform_request(
            Feature.URL, params=params)
        self._features = features.json()

    def fetch(self) -> "Dataset":
        """Fetches metadata related to the Dataset"""

        super().fetch()
        self._fetch_features()

        return self

    @property
    def features(self):
        """Return a list with all the features of the dataset"""
        if not self._fetched:
            self.fetch()
        return self._features

    @property
    def version(self):
        """Return the current version of the dataset"""
        if self._version is None:
            v = self._client._perform_request(url=Version.URL, params=dict(
                dataset=self.code)).json()

            if len(v) != 1:
                raise ValueError(
                    'Not found versions associated with this dataset')

            self._version = Version(client=self._client, **v[0])

        return self._version

    def to_pandas(self):
        files = self.version.get_files(filetype='parquet')

        if not files:
            raise ValueError(
                'The content of the dataset is not found. '
                'Perhaps the version you are trying to download is no longer available on the server.')

        df_list = []
        for file in files:
            url = file.url
            df = pd.read_parquet(url)
            df_list.append(df)

        if len(df_list) > 1:
            df = pd.concat(df_list)

        return df

    def to_geopandas(self):
        if not _has_geopandas:
            raise ImportError(
                "geopandas is required to load a dataset with geometries")

        files = self.version.get_files(filetype='geoparquet')

        if not files:
            raise ValueError('Not dataset found')

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
