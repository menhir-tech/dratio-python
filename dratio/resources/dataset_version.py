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
This module contains the Version class used to represent a file in the database.
"""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


from .base import DatabaseResource

if TYPE_CHECKING:  # Type hints
    import pandas as pd

    from .dataset import Dataset
    from .dataset_file import File

__all__ = ["Version"]


class Version(DatabaseResource):
    """Version of a dataset in the database

    Parameters
    ----------
    code : str
       Unique identifier of the feature in the database.
    client: Client
        Client object used to perform requests to the database.
    **kwargs
        Additional keyword arguments used to initialize the metadata information.

    """

    _URL = "version/"

    @property
    def name(self) -> Union[str, None]:
        """Name of the version"""
        return self.metadata.get("name")

    @property
    def description(self) -> Union[str, None]:
        """Description of the version"""
        return self.metadata.get("description")

    @property
    def dataset(self) -> "Dataset":
        """Dataset to which the version belongs"""

        dataset_code = self.metadata.get("dataset", {}).get("code")
        return self._client.get_dataset(code=dataset_code)

    def list_files(
        self,
        filetype: Optional[Literal["parquet", "geoparquet"]] = None,
        format: Literal["pandas", "json", "api"] = "pandas",
    ) -> Union["pd.DataFrame", List[Dict[str, Any]], List["File"]]:
        """Returns a list of files associated to the version.

        Parameters
        ----------
        filetype : Optional[Literal["parquet", "geoparquet"]]
            Type of file to filter. If None, all files are returned.
        format: Literal["pandas", "json"]
            Format of the returned list, either a list of dictionaries or a
            pandas DataFrame.

        Returns
        -------
        Literal["pandas", "json"]
            List of files associated to the version.
        """
        return self._client.list(
            kind="file", format=format, version=self.code, filetype=filetype
        )
