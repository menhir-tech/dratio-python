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

from typing import Any, Dict, TYPE_CHECKING

from ..exceptions import ObjectNotFound

if TYPE_CHECKING:
    from ..client import Client


class DatabaseResource:
    """
    Abstract base class for database objects (e.g., Dataset, Feature, and Publisher).
    Encapsulates common logic for retrieving and interacting with objects in the database.

    Parameters
    ----------
    code : str
        Unique identifier of the object in the database.
    client : Client
        Client instance used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information.

    Attributes
    ----------
    _URL : str
        Relative URL for making requests to the database (class attribute).
        (For internal usage).

    Notes
    -----
    This class is intended for internal API use. See the `Client` and `Dataset`
    classes for more information.
    """

    def __init__(self, code: str, client: "Client", **kwargs):
        """
        Initializes the object with the provided code and client instance.
        """
        self.code = code
        self._client = client
        self._fetched = False
        self._metadata = {**kwargs}

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.
        """
        return f"{self.__class__.__name__}('{self.code}')"

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Retrieves the metadata associated with the object.

        Notes
        -----
        The first time this property is accessed, a request is made to the server to
        fetch the metadata. Subsequent accesses return the previously loaded information.
        To update the metadata, create a new instance of the object.
        """
        if not self._fetched:
            self.fetch()

        return self._metadata

    def __getitem__(self, key: str) -> Any:
        """
        Provides a convenient way to access metadata attributes directly from the object.
        """
        return self.metadata[key]

    def fetch(self) -> "DatabaseResource":
        """
        Updates the metadata dictionary of the object by performing an HTTP request
        to the server.

        Returns
        -------
        self : DatabaseResource
            The object itself.

        Notes
        -----
        This method modifies the object's internal state.

        Raises
        ------
        requests.exceptions.RequestException
            If the request fails.
        ObjectNotFound
            If the object is not found in the database.
        """
        relative_url = f"{self._URL}/{self.code}/"
        response = self._client._perform_request(relative_url, allowed_status=[404])

        if response.status_code == 404:
            raise ObjectNotFound(self.__class__.__name__, self.code)

        self._metadata = response.json()
        self._fetched = True

        return self
