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
This module contains the Version class used to represent a file in the database.
"""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from .mixins import NameDescriptionMixin

from .base import DatabaseResource

if TYPE_CHECKING:  # Type hints
    from pathlib import Path

    import pandas as pd
    import geopandas as gpd

    from .dataset import Dataset
    from .dataset_file import File


__all__ = ["Version"]


class Version(DatabaseResource, NameDescriptionMixin):
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
    def dataset(self) -> "Dataset":
        """Dataset to which the version belongs"""

        dataset_code = self.metadata.get("dataset", {}).get("code")
        return self._client.get_dataset(code=dataset_code)

    def upload_file(
        self,
        file: Union[str, "Path", "pd.DataFrame", "gpd.GeoDataFrame"],
        filetype: Optional[Literal["parquet", "geoparquet"]] = None,
        update: bool = False,
    ):
        """Uploads a file to the version.

        Returns
        -------
        File
            File object representing the uploaded file.
        """
        from ..provider.file_upload import _infer_filetype, _upload_file

        url = f"{self._URL}{self.code}/upload/"
        filetype = _infer_filetype(file, filetype)

        content = self._client._perform_request(
            url, method="POST", json={"update": update, "filetype": filetype}
        ).json()

        url = content["url"]
        file_code = content["code"]
        version_code = content["version"]

        _upload_file(file=file, filetype=filetype, url=url)

        new_file = self._client.get_file(code=file_code)
        new_file._update_availability()

        return new_file

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
