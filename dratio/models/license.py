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
This module contains the license and license item classes.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Union
from .mixins import NameDescriptionMixin, ListDatasetsMixin, ListFeaturesMixin, ListPublisherMixin

from .base import DatabaseResource

try: # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

if TYPE_CHECKING:
    import pandas as pd

__all__ = ["License", "LicenseItem"]


class License(DatabaseResource, ListFeaturesMixin, ListDatasetsMixin, ListPublisherMixin, NameDescriptionMixin):
    """
    Class to represent a category in the database.
    """

    _URL = "license/"
    _FILTER_KEYWORD = "license"
    _LIST_FIELDS = ["code", "name", "url"]
    _EDITABLE_FIELDS = ["code", "name", "url", "description",
                        "name_es", "description_es", "is_public"]

    @property
    def license_items(self) -> List["LicenseItem"]:
        """
        Get the license items of the license.
        """
        if not hasattr(self, "_license_items"):
            self._license_items = None

        if self._license_items is None:
            items = self._client.list(
                kind="license-item", license=self.code, format="api")
            # converts as a dict with code as key
            items = {item.code.split('--')[-1]: item for item in items}
            self._license_items = items

        return self._license_items

    def list_license_items(
        self, format: Literal["pandas", "json", "api"] = "pandas"
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["LicenseItem"]]:
        """
        List the license items of the license.
        """
        return self._client.list(kind="license-item", format=format, license=self.code)

    def add_license_item(self,
                         code: str,
                         name: str,
                         description: str,
                         grant: bool = None,
                         name_es: str = None,
                         description_es: str = None,
                         is_public: bool = True
                         ) -> "LicenseItem":
        """
        Add or overrides a license item to the license.

        To add a license item to a license and save it in the database, you will
        need to have edit or create permissions on the license.

        Parameters
        ----------
        code : str
            The code of the license item. The code 

        Notes
        -----
        You will need to save the license to preserve the changes, including
        the new license item.

        """
        item = self.license_items.get(code)
        if item is None:
            item = self._client.get(code=code, kind="license-item")

        item['name'] = name
        item['description'] = description
        item['grant'] = grant
        item['name_es'] = name_es
        item['description_es'] = description_es
        item['is_public'] = is_public
        item['license'] = self.code

        self.license_items[code] = item

        return item

    def _save_subresources(self) -> None:
        """
        Save the license items.
        """

        super()._save_subresources()

        # Save the license items
        for item in self.license_items.values():
            item['license'] = self.code
            item.save()


class LicenseItem(DatabaseResource, NameDescriptionMixin):
    """
    Class to represent a license item in the database.
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
        'license',
        'order'
    ]

    @ property
    def license(self) -> "License":
        """
        Get the license of the license item.
        """
        return self._client.get(code=self.metadata.get("license"), kind="license")
