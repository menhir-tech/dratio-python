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
Client functionality, common across all API requests.
"""

from typing import Any, Dict, List, Union, Optional

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import pandas as pd
import requests
from requests.compat import urljoin
import warnings
import re

from .resources.dataset import Dataset
from .resources.feature import Feature
from .resources.publisher import Publisher
from .resources.dataset_version import Version
from .resources.dataset_file import File

from .__version__ import __version__
from .utils import _format_list_response


class Client:
    """Client to interact with dratio.io API

    Parameters
    ----------
    key : str
        API key to access dratio.io API. You can obtain your API key at
        https://dratio.io/app/api. Please, keep this key in a safe place.
    persistent_session : bool, optional
        Whether to use a persistent session to perform requests to the API.
        Defaults to True.


    Examples
    --------

    Retrieve datasets available in the dratio.io marketplace as a pandas dataframe:

    >>> from dratio import Client
    >>> client = Client(key='<your_api_key>')
    >>> df_datasets = client.get_datasets()


    Retrieve a dataset from the dratio.io marketplace:

    >>> dataset = client.get(code='unemployment-municipality')
    >>> dataset
    Dataset('unemployment-municipality')

    Access fields included in the metadata of the dataset:

    >>> dataset["description"]
    'Monthly data on the number of unemployed persons by municipality, ...'

    Download a dataset as a pandas dataframe:

    >>> df = dataset.to_pandas()


    """

    BASE_URL = "https://api.dratio.io/api/"
    _KEY_REGEX = r"^[a-z0-9]{64}$"

    _FEATURE_CLASS = Feature
    _PUBLISHER_CLASS = Publisher
    _FILE_CLASS = File
    _DATASET_CLASS = Dataset
    _VERSION_CLASS = Version
    

    def __init__(self, key: str, *, persistent_session: bool = True) -> "Client":
        """Initializes the Client object"""
        self._base_url = Client.BASE_URL
        self.persistent_session = persistent_session
        self._current_session = None
        self.key = key

        self._check_key(key)

    def __repr__(self) -> str:
        """Represents Client object as a string"""
        return f"Client('{self.key[:6]}...')"

    def _check_key(self, key: str) -> None:
        """Checks that the API key is not empty"""
        if not isinstance(key, str):
            raise TypeError(f"key must be a string, not {type(key)}.")

        if not re.match(Client._KEY_REGEX, key):
            raise ValueError(
                "key must be a 64-character string of lowercase and numbers. "
                "Are you sure you are using a correct key? "
                "You can obtain a new API key at https://dratio.io/app/api/."
            )

    @property
    def _session(self) -> requests.Session:
        """Authenticated session to perform requests to the API (requests.Session).
        If persistent_session is True, the session is created once and reused.
        """
        if self._current_session is None:
            session = requests.Session()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {self.key}",
            }
            session.headers = headers
            if self.persistent_session:
                self._current_session = session
        else:
            session = self._current_session

        return session

    def _perform_request(
        self, url: str, allowed_status: List[int] = [], **kwargs
    ) -> requests.Response:
        """Performs a request to the API.

        Parameters
        ----------
        url : str
            Relative URL to perform the request to.
        allowed_status : List[int], optional
            List of allowed status codes. If the status code of the response is
            not in this list and is different than 200 Ok, a requests.HTTPError
            is raised. Defaults to [].
        **kwargs
            Keyword arguments to pass to requests.Session.get

        Returns
        -------
        requests.Response
            Response from the API.

        Raises
        ------
        requests.HTTPError
            If the status code of the response is not in `allowed_status` and is
            different than `200 Ok`.
        """
        url = urljoin(self._base_url, url)

        response = self._session.get(url=url, **kwargs)

        if response.status_code not in allowed_status:
            response.raise_for_status()

        return response

    def info(self) -> Dict[str, str]:
        f"""Returns information about the dratio.io API.

        Returns
        -------
        Dict[str, str]:
            Dictionary with information about the dratio.io API, containing
            the backend version and the client version.

        Examples
        --------

        >>> from dratio import Client
        >>> client = Client('Your API key')
        >>> client.info()
        {{'version': '0.0.1', 'client_version': '{__version__}'}}

        """
        response = self._perform_request(url="")
        response.raise_for_status()

        # Add client version to the response
        info_data = response.json()
        info_data["client_version"] = __version__

        return info_data

    def get(
        self,
        code: str,
        version: str = None,
        kind: Literal["dataset", "feature", "publisher"] = "dataset",
    ) -> Union[Dataset, Feature]:
        """Returns a Dataset object with the information associated with the
        dataset through which the information can be downloaded.

        Parameters
        ----------
        code : str
            Unique identificador for a dataset in the database.
            Codes can be searched in the dratio.io marketplace or
            by using `get_datasets`.
        version : str, optional
            Version of the object to retrieve. If not specified, the latest
            version is retrieved. Defaults to None.
        kind : Literal["dataset", "feature", "publisher"]
            Kind of object to retrieve. Defaults to "dataset".

        Returns
        -------
        Union[Dataset, Feature]
            If kind=='dataset', returns a Dataset object with the information
            associated with the dataset through which the information can be
            downloaded. If kind=='feature', returns a Feature object with the
            information associated with the feature through which the
            information can be downloaded.
            If kind=='publisher', returns a Publisher object with the
            information associated with the publisher through which the
            information can be downloaded.

        Examples
        --------

        Retrieve a dataset from the dratio.io marketplace:

        >>> from dratio import Client
        >>> client = Client('Your API key')
        >>> dataset = client.get(code='municipalities')
        >>> dataset
        Dataset('municipalities')

        Download a dataset as a pandas dataframe:

        >>> df_municipalities = dataset.to_pandas()

        Retrieve a publisher from the dratio.io marketplace:

        >>> publisher = client.get(code='ine', kind='publisher')
        >>> publisher
        Publisher('ine')

        Get the datasets published by the INE:

        >>> datasets = publisher.list_datasets()


        Raises
        ------
        ValueError
            If kind is not 'dataset', 'feature' or 'publisher'.

        """
        if kind == "dataset":
            return Dataset(client=self, code=code, version=version)
        elif kind == "feature":
            return Feature(client=self, code=code, version=version)
        elif kind == "publisher":
            raise NotImplementedError("Publisher is not implemented yet.")

        raise ValueError("kind must be either 'dataset' or 'feature'.")

    def get_dataset(self, code: str, version: str = None) -> Dataset:
        """Returns a Dataset object with the information associated with the
        dataset through which the information can be downloaded.

        Parameters
        ----------
        code : str
            Unique identificador for a dataset in the database.
            Codes can be searched in the dratio.io marketplace or
            by using `get_datasets`.

        Returns
        -------
        Dataset
            Dataset object with the information associated with the
            dataset through which the information can be downloaded.

        """

        return Client._DATASET_CLASS(client=self, code=code, version=version)

    def get_publisher(self, code: str, version: Optional[str] = None):
        """Returns a Dataset object with the information associated with the
        dataset through which the information can be downloaded.

        Parameters
        ----------
        code : str
            Unique identificador for a dataset in the database.
            Codes can be searched in the dratio.io marketplace or
            by using `get_datasets`.

        Returns
        -------
        Dataset
            Dataset object with the information associated with the
            dataset through which the information can be downloaded.

        """
        if version is not None:
            warnings.warn("Version parameter is ignored when retrieving a publisher.")

        return Client._PUBLISHER_CLASS(client=self, code=code)

    def get_feature(self, code: str, version: Optional[str] = None) -> "Feature":
        """Returns a Dataset object with the information associated with the
        dataset through which the information can be downloaded.

        Parameters
        ----------
        code : str
            Unique identificador for a dataset in the database.
            Codes can be searched in the dratio.io marketplace or
            by using `get_datasets`.

        Returns
        -------
        Dataset
            Dataset object with the information associated with the
            dataset through which the information can be downloaded.

        """
        return Client._FEATURE_CLASS(client=self, code=code, version=version)
    
    def get_file(self, code: str) -> "File":
        """Returns a File object with the information associated with a
        dataset stored file through which the information can be downloaded.

        Parameters
        ----------
        code : str
            Unique identificador for a file in the database.
            Codes can be searched in the dratio.io marketplace or
            by using `list_files` methods of a dataset.

        Returns
        -------
        Dataset
            Dataset object with the information associated with the
            dataset through which the information can be downloaded.

        """
        return Client._FILE_CLASS(client=self, code=code)
    
    def _get_dataset_version(self, code: str) -> "Version":
        """Returns a Version object with the information associated with the
        version of a dataset.

        Parameters
        ----------
        code : str
            Unique identificador for a dataset version in the database.
            Codes can be searched in the dratio.io marketplace or
            by using `get_datasets`.

        Returns
        -------
        Version
            Version object with the information associated with the
            latest version of the dataset.

        """
        return Client._VERSION_CLASS(client=self, code=code)

    def list_datasets(
        self,
        format: Literal["pandas", "json"] = "pandas",
        publisher: Optional[str] = None,
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """Returns a dataframe or a list with information of the datasets available in the dratio.io marketplace.

        Parameters
        ----------
        format : Literal['pandas', 'json'], optional
            Format of the output. Defaults to 'pandas'.

        Returns
        -------
        Union[pd.DataFrame, List[Dict[str, Any]]]
            List of datasets available in the dratio.io marketplace, as
            a pandas dataframe or a list of dictionaries depending on the
            value of `format`.

        Raises
        ------
        ValueError
            If `format` is not 'pandas' or 'json'.
        HTTPError
            In case of any error when performing the request to the API.

        Examples
        --------

        >>> from dratio import Client
        >>> client = Client("Your API key")
        >>> df_datasets = client.list_datasets()

        """
        params = {}
        if publisher is not None:
            params["publisher"] = publisher

        kwargs = {} if not len(params) else {"params": params}

        datasets = self._perform_request(Client._DATASET_CLASS._URL, **kwargs).json()
        return _format_list_response(
            datasets, format=format, fields=Client._DATASET_CLASS._LIST_FIELDS
        )

    def list_features(
        self,
        format: Literal["pandas", "json"] = "pandas",
        publisher: Optional[str] = None,
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """Returns a dataframe or a list with information of the features available in the dratio.io marketplace.

        Parameters
        ----------
        format : Literal['pandas', 'json'], optional
            Format of the output. Defaults to 'pandas'.

        Returns
        -------
        Union[pd.DataFrame, List[Dict[str, Any]]]
            List of datasets available in the dratio.io marketplace, as
            a pandas dataframe or a list of dictionaries depending on the
            value of `format`.

        Raises
        ------
        ValueError
            If `format` is not 'pandas' or 'json'.
        HTTPError
            In case of any error when performing the request to the API.

        Examples
        --------

        >>> from dratio import Client
        >>> client = Client("Your API key")
        >>> df_features = client.list_features()

        """

        params = {}
        if publisher is not None:
            params["publisher"] = publisher

        kwargs = {} if not len(params) else {"params": params}

        features = self._perform_request(Client._FEATURE_CLASS._URL, **kwargs).json()
        return _format_list_response(
            features, format=format, fields=Client._FEATURE_CLASS._LIST_FIELDS
        )

    def list_publishers(
        self,
        format: Literal["pandas", "json"] = "pandas",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """Returns a dataframe or a list with information of the features available in the dratio.io marketplace.

        Parameters
        ----------
        format : Literal['pandas', 'json'], optional
            Format of the output. Defaults to 'pandas'.

        Returns
        -------
        Union[pd.DataFrame, List[Dict[str, Any]]]
            List of features available in the dratio.io marketplace, as
            a pandas dataframe or a list of dictionaries depending on the
            value of `format`.

        Raises
        ------
        ValueError
            If `format` is not 'pandas' or 'json'.
        HTTPError
            In case of any error when performing the request to the API.

        Examples
        --------

        >>> from dratio import Client
        >>> client = Client("Your API key")
        >>> df_publishers = client.list_publishers()

        """
        publishers = self._perform_request(Client._PUBLISHER_CLASS._URL).json()
        return _format_list_response(
            publishers, format=format, fields=Client._PUBLISHER_CLASS._LIST_FIELDS
        )
