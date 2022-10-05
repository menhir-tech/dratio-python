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

from typing import Any, Literal, Union

import pandas as pd
import requests
from requests.compat import urljoin

from .dataset import Dataset


class Client:
    """Performs requests to the dratio.io web services."""
    BASE_URL = "https://dratio.io/api/"

    def __init__(self, key: str, *, persistent_session: bool = True) -> "Client":
        """
        :param key: Dratio API key. Required. Key for authorization
            and authentication purposes.
        :type key: string

        :param persistent_session: Indicates whether a persistent session
            should be used for all requests or whether a new one should be 
            created for each request.
        :type key: bool

        """
        self._base_url = Client.BASE_URL
        self.persistent_session = persistent_session
        self._current_session = None
        self.key = key

    def __repr__(self) -> str:
        """Represents Client object as a string"""
        return f"Client('{self.key[:8]}...')"

    @property
    def _session(self) -> requests.Session:
        """
        Returns an authenticated session to perform requests.
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
        """
        Wrapper to perform GET requests to dratio.io API.

        :param url: Relative url to perform the http request.
        :type key: string

        :param allowed_status: List of allowed HTTP statuses. 
            In case of receiving a response with a status not included in 
            the list or different from 200 OK, an HTTPError will be raised.
        :type key: list[int]
        """
        url = urljoin(self._base_url, url)

        response = self._session.get(url=url, **kwargs)

        if response.status_code not in allowed_status:
            response.raise_for_status()

        return response

    def get(self, code: str) -> Dataset:
        """Retrieves a Dataset"""

        return Dataset(client=self, code=code)

    def get_datasets(self, format: Literal['pandas', 'json'] = 'pandas') -> Union[pd.DataFrame, list[dict[str, Any]]]:
        datasets = self._perform_request(Dataset.URL).json()

        if format == 'pandas':
            datasets = pd.json_normalize(datasets)

        return datasets
