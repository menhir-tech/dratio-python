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

from typing import Any, Union

try: # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import pandas as pd
import requests
from requests.compat import urljoin

from .base import Dataset


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

    def __init__(self, key: str, *, persistent_session: bool = True) -> "Client":
        """Initializes the Client object"""
        self._base_url = Client.BASE_URL
        self.persistent_session = persistent_session
        self._current_session = None
        self.key = key

    def __repr__(self) -> str:
        """Represents Client object as a string"""
        return f"Client('{self.key[:6]}...')"

    @property
    def _session(self) -> requests.Session:
        """Authenticated session to perform requests to the API (requests.Session).
        If persistent_session is True, the session is created once and reused.
        """
        if self._current_session is None:
            session = requests.Session()
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'Token {self.key}'}
            session.headers = headers
            if self.persistent_session:
                self._current_session = session
        else:
            session = self._current_session

        return session

    def _perform_request(self,
                         url: str,
                         allowed_status: list[int] = [],
                         **kwargs) -> requests.Response:
        """Performs a request to the API.

        Parameters
        ----------
        url : str
            Relative URL to perform the request to.
        allowed_status : list[int], optional
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

    def get(self, code: str) -> Dataset:
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

        return Dataset(client=self, code=code)

    def get_datasets(self, format: Literal['pandas', 'json'] = 'pandas') -> Union[pd.DataFrame, list[dict[str, Any]]]:
        """Returns a dataframe or a list with information of the datasets available in the dratio.io marketplace.

        Parameters
        ----------
        format : Literal['pandas', 'json'], optional
            Format of the output. Defaults to 'pandas'.

        Returns
        -------
        Union[pd.DataFrame, list[dict[str, Any]]]
            List of datasets available in the dratio.io marketplace.

        Raises
        ------
        ValueError
            If `format` is not 'pandas' or 'json'.
        """
        if format not in ['pandas', 'json']:
            raise ValueError(
                f"format must be 'pandas' or 'json', not {format}")

        datasets = self._perform_request(Dataset._URL).json()

        if format == 'pandas':
            datasets = pd.json_normalize(datasets)

        return datasets
