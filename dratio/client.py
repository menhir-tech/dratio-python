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
Client to interact with dratio.io API
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import re
import warnings

import requests
from requests.compat import urljoin

from .__version__ import __version__
from .resources import Dataset, Feature, File, Publisher, Version
from .resources.category import (Category, DataLevel, PusblisherType, Scope,
                                 Unit)
from .resources.license import License, LicenseItem
from .utils import _get_params_from_kwargs, _warn_param_used

if TYPE_CHECKING:
    import pandas as pd

    from .resources.base import DatabaseResource


__all__ = ["Client"]

CLASSES_MAPPING = {
    "dataset": Dataset,
    "feature": Feature,
    "file": File,
    "publisher": Publisher,
    "version": Version,
    "category": Category,
    "scope": Scope,
    "unit": Unit,
    "publisher-type": PusblisherType,
    "data-level": DataLevel,
    "license": License,
    "license-item": LicenseItem,
}

DatabaseResourceLiteral = Literal[
    "dataset",
    "feature",
    "file",
    "publisher",
    "version",
    "category",
    "scope",
    "unit",
    "publisher-type",
    "data-level",
    "license",
    "license-item",
]


class Client:
    """Client to interact with dratio.io API

    Parameters
    ----------
    key : str
        API key to access dratio.io API. You can obtain your API key at
        https://dratio.io/app/api/. Please, keep this key in a safe place.
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

    _CLASSES_MAPPING = CLASSES_MAPPING

    def __init__(self, key: str, *, persistent_session: bool = True) -> "Client":
        """Initializes the Client object"""
        self._base_url = Client.BASE_URL
        self.persistent_session = persistent_session
        self._current_session = None
        self.key = key
        self._compatibility_checked = False

        # Offline check of the format of the API key
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
                "key must be a 64-character string of lowercase and numbers.\n"
                "Are you sure you are using a correct key?\n"
                "You can obtain a new API key at https://dratio.io/app/api/."
            )

    def _check_client_compatibility(self) -> None:
        """Checks that the client is compatible with the API version"""

        info = self.info()

        if info["client_version"] not in info.get("client_compatibility", []):
            warnings.warn(
                f"The client version ({__version__}) is not compatible with the "
                f"API version ({info['version']}).\nPlease, update the client "
                f"to the latest version with `pip install dratio --upgrade`.\n"
                f"Possibly some functionalities may not work properly."
            )

    @classmethod
    def _resolve_class(cls, name: str) -> Type["DatabaseResource"]:
        """
        Given a class and a name, returns the corresponding class.

        Parameters
        ----------
        name : str
            Name of the class to resolve.

        Returns
        -------
        Type[DatabaseResource]
            Class corresponding to the name.

        Raises
        ------
        ValueError
            If the name is not a valid class.
        """
        resource_class = cls._CLASSES_MAPPING.get(name)

        if resource_class is None:
            raise ValueError(
                f"Invalid resource name: {name}.\n"
                f"Valid resource names are: {list(cls._CLASSES_MAPPING.keys())}.\n"
            )

        return resource_class

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
        if not self._compatibility_checked:
            self._compatibility_checked = True
            self._check_client_compatibility()

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
        {{'version': '0.0.1', 'client_version': '{__version__}', ...}}

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
        kind: DatabaseResourceLiteral = "dataset",
    ) -> "DatabaseResource":
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
        # Relax the type of code to allow None for internal use
        if code is None:
            return None

        resource_cls = Client._resolve_class(kind)

        if kind == "dataset":
            return resource_cls(client=self, code=code, version=version)

        _warn_param_used(version, "version")

        return resource_cls(client=self, code=code)

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
        return self.get(code=code, kind="dataset", version=version)

    def get_publisher(self, code: str):
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
        return self.get(code=code, kind="publisher")

    def get_feature(self, code: str) -> "Feature":
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
        return self.get(code=code, kind="feature")

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
        return self.get(code=code, kind="file")

    def list(
        self,
        kind: DatabaseResourceLiteral = "dataset",
        format: Literal["pandas", "json", "api"] = "pandas",
        **kwargs,
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["DatabaseResource"]]:
        """List a resource from the dratio.io marketplace.

        This method is generic and can be used to list any resource from the
        dratio.io marketplace. The resource to list can be specified with the
        `kind` parameter. The available resources are:

        - `dataset`: List datasets.
        - `feature`: List features.
        - `publisher`: List publishers.
        - `file`: List files.
        - `version`: List versions.

        The main objects of Dratio are `Dataset`, `Publisher`, `Feature` and `File`.
        These objects can be listed with their corresponding methods: `list_datasets`,
        `list_publishers`, `list_features` and `list_files`.

        Parameters
        ----------
        kind : Literal['dataset', 'feature', 'publisher', 'file', 'version'], optional
            Kind of resource to list.
        format : Literal['pandas', 'json', 'api'], optional
            Format of the output. Defaults to 'pandas'.
        **kwargs
            Additional parameters to filter the resources.

        Returns
        -------
        Union[pd.DataFrame, List[Dict[str, Any]], List[DatabaseResource]]
            List of resources available in the dratio.io marketplace, as
            a pandas dataframe, a list of dictionaries or a list of
            DatabaseResource objects depending on the value of `format`.

        Raises
        ------
        ValueError
            If `kind` is not an available resource.
        HTTPError
            In case of any error when performing the request to the API.

        Examples
        --------

        >>> from dratio import Client
        >>> client = Client('Your API key')

        List datasets as a pandas dataframe:

        >>> df_datasets = client.list(kind='dataset', format='pandas')

        List features as a list of dictionaries:

        >>> features = client.list(kind='feature', format='json')

        List publishers as a list of `Publisher` objects:

        >>> publishers = client.list(kind='publisher', format='api')

        """
        params = _get_params_from_kwargs(**kwargs)

        resource_cls = Client._resolve_class(kind)
        return resource_cls._list(client=self, format=format, **params)

    def list_datasets(
        self,
        format: Literal["pandas", "json", "api"] = "pandas",
        publisher: Optional[str] = None,
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Dataset"]]:
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

        List all datasets as a pandas dataframe:

        >>> df_datasets = client.list_datasets()

        List all datasets of a publisher:

        >>> df_datasets = client.list_datasets(publisher="ine")


        """
        return self.list(kind="dataset", format=format, publisher=publisher)

    def list_features(
        self,
        format: Literal["pandas", "json", "api"] = "pandas",
        dataset: Optional[str] = None,
        publisher: Optional[str] = None,
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Feature"]]:
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

        return self.list(
            kind="feature", format=format, dataset=dataset, publisher=publisher
        )

    def list_publishers(
        self,
        format: Literal["pandas", "json", "api"] = "pandas",
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["Publisher"]]:
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

        return self.list(kind="publisher", format=format)
