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
This module contains the tags classes. A publisher is an data source 
from which datasets are obtained.
"""

from .base import DatabaseResource
from typing import List, Literal, Union, Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


__all__ = ["License", "LicenseItem"]


class License(DatabaseResource):
    """
    Class to represent a category in the database.
    """

    _URL = "license/"
    _LIST_FIELDS = ["code", "name", "url"]

    def list_license_items(
        self, format: Literal["pandas", "json", "api"] = "pandas"
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["LicenseItem"]]:
        """
        List the license items of the license.
        """
        return self._client.list(kind="license-item", format=format, license=self.code)


class LicenseItem(DatabaseResource):
    """
    Class to represent a license itemp in the database.
    """

    _URL = "license-item/"
    _LIST_FIELDS = ["code", "name", "license", "grant"]
    _EDITABLE_FIELDS = [
        "code",
        "name",
        "description",
        "grant",
        "name_es",
        "description_es",
        "is_public",
    ]

    @property
    def license(self) -> "License":
        """
        Get the license of the license item.
        """
        return self._client.get(code=self.metadata.get("license"), kind="license")
