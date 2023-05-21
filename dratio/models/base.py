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
Base class for database objects.
"""
from typing import TYPE_CHECKING, Any, Dict, List, Union

from ..exceptions import ObjectNotFound
from ..utils import _format_list_response

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

if TYPE_CHECKING:
    import pandas as pd

    from ..client import Client

__all__ = ["DatabaseResource"]

# Constants
NOT_FOUND_STATUS = 404


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

    _LIST_FIELDS = None
    _EDITABLE_FIELDS = None

    def __init__(self, code: str, client: "Client", **kwargs):
        """
        Initializes the object with the provided code and client instance.
        """
        self.code = code
        self._client = client
        self._fetched = False
        self._metadata = {"code": code, **kwargs}
        self._exists = None

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

    def _check_value(self, key: str, value: Any) -> Any:
        """
        Used in inherited classes to check the value of a metadata attribute
        """
        pass

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Provides a convenient way to set metadata attributes directly from the object.
        """
        if self._EDITABLE_FIELDS is None or key in self._EDITABLE_FIELDS:
            if not self._fetched:
                self.fetch(fail_not_found=False)

            # Objects are referenced by their code
            if hasattr(value, "code"):
                value = value.code

            # Check value
            self._check_value(key, value)

            self.metadata[key] = value
        else:
            raise AttributeError(
                f"Attribute '{key}' is not editable."
                f" Editable attributes are: {self._EDITABLE_FIELDS}."
            )

    def fetch(self, fail_not_found: bool = True) -> "DatabaseResource":
        """
        Updates the metadata dictionary of the object by performing an HTTP request
        to the server.

        Returns
        -------
        self : DatabaseResource
            The object itself.
        fail_not_found : bool, default True
            Whether to raise an exception if the object is not found in the database.

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
        response = self._client._perform_request(
            relative_url, allowed_status=[NOT_FOUND_STATUS]
        )

        if response.status_code == NOT_FOUND_STATUS:
            self._exists = False
            if fail_not_found:
                raise ObjectNotFound(self.__class__.__name__, self.code)
        else:
            self._exists = True
            self._metadata = response.json()

        self._fetched = True

        return self

    def describe(self) -> str:
        """
        Returns a string representation of the object's metadata.
        """
        raise NotImplementedError

    @classmethod
    def _list(
        cls,
        client: "Client",
        format: Literal["pandas", "json", "api"] = "pandas",
        **kwargs,
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["DatabaseResource"]]:
        """
        Returns a list of objects of the given type.

        Parameters
        ----------
        client : Client
            Client instance used to perform requests to the database.
        format : {"pandas", "json", "api"}, default "pandas"
            Format of the returned list. If "pandas", a pandas DataFrame is returned.
            If "json", a JSON object is returned. If "api", a list of dictionaries
            is returned.
        **kwargs
            Additional keyword arguments used to filter the list of objects.
        """

        response = client._perform_request(cls._URL, params=kwargs)
        data = response.json()

        data = _format_list_response(
            data, format=format, fields=cls._LIST_FIELDS, client=client, cls=cls
        )

        return data
    
    def keys(self) -> List[str]:
        """
        Returns the keys of the metadata dictionary.
        """
        return list(self.metadata.keys())

    def _save_subresources(self) -> None:
        """Saves the subresources of the object."""
        pass

    def save(self) -> "DatabaseResource":
        """
        Saves the object's metadata to the database.

        Returns
        -------
        self : DatabaseResource
            The object itself.


        Raises
        ------
        requests.exceptions.RequestException
            If the request fails.
        """
        if not self._fetched:
            self.fetch(fail_not_found=False)

        if self._exists:
            relative_url = f"{self._URL}/{self.code}/"
            method = "PATCH"

        else:
            relative_url = f"{self._URL}/"
            self._metadata["code"] = self.code
            method = "POST"

        self._client._perform_request(relative_url, method=method, json=self.metadata)
        self._save_subresources()
        self.fetch(fail_not_found=True)

    def delete(self) -> None:
        """
        Deletes the object from the database.

        Raises
        ------
        requests.exceptions.RequestException
            If the request fails.
        """

        relative_url = f"{self._URL}/{self.code}/"
        self._client._perform_request(relative_url, method="DELETE")
        self._exists = False
