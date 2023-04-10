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
Functionalities to manage file uploads
"""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryFile
from typing import TYPE_CHECKING, BinaryIO, Literal, Optional, Union

import geopandas as gpd
import pandas as pd
import requests

__all__ = ["_infer_filetype", "_upload_file"]

# Allowed filetypes for upload
ALLOWED_FILETYPES = ["parquet", "geoparquet", "csv", "json"]
GEOMETRIC_FILETYPES = ["geoparquet"]


def _infer_filetype(
    file: Union[str, "Path", "pd.DataFrame", "gpd.GeoDataFrame"],
    filetype: Optional[str] = None,
) -> str:
    """Infer the filetype from the file or the filetype parameter"""
    if filetype is not None:
        if filetype not in ALLOWED_FILETYPES:
            raise ValueError(
                f"Invalid Filetype. Allowed filetypes are: {ALLOWED_FILETYPES}"
            )
        return filetype

    if isinstance(file, gpd.GeoDataFrame):
        return "geoparquet"
    elif isinstance(file, pd.DataFrame):
        return "parquet"

    else:
        file = Path(file)
        suffix = file.suffix[1:]
        if suffix not in ALLOWED_FILETYPES:
            raise ValueError(
                f"Cannot determine filetype, specify using the filetype."
                f" Allowed filetypes are: {ALLOWED_FILETYPES}."
            )
        return suffix


def _upload_file(
    file: Union[str, "Path", "pd.DataFrame", "gpd.GeoDataFrame"],
    filetype: str,
    url: str,
):
    """Uploads a file to a given url using multipart upload"""
    with stream_file(file, filetype) as f:
        put_file(url, f)


@contextmanager
def stream_file(
    file: Union[str, "Path", "pd.DataFrame", "gpd.GeoDataFrame"],
    filetype: Optional[str] = None,
):
    try:
        f = None
        # GeoDataFrame
        if isinstance(file, gpd.GeoDataFrame):
            if filetype not in GEOMETRIC_FILETYPES:
                raise ValueError(
                    f"Invalid Filetype for GeodataFrame. "
                    f"Allowed filetypes are: {GEOMETRIC_FILETYPES}"
                )
            if filetype == "geoparquet":
                f = TemporaryFile()
                file.to_parquet(f)
                f.flush()
                f.seek(0)

        # DataFrame
        elif isinstance(file, pd.DataFrame):
            if filetype not in ALLOWED_FILETYPES or filetype in GEOMETRIC_FILETYPES:
                raise ValueError(
                    f"Invalid Filetype for DataFrame. "
                    f"Allowed filetypes are: {ALLOWED_FILETYPES} excluding {GEOMETRIC_FILETYPES}"
                )
            if filetype == "parquet":
                f = TemporaryFile()
                file.to_parquet(f)
                f.flush()
                f.seek(0)
            elif filetype == "csv":
                f = TemporaryFile()
                file.to_csv(f)
                f.flush()
                f.seek(0)
            elif filetype == "json":
                f = TemporaryFile()
                file.to_json(f, orient="records")
                f.flush()
                f.seek(0)
        # Path or str
        else:
            file = Path(file)
            if not file.exists():
                raise FileNotFoundError(f"File {file} does not exist")
            f = open(file, "rb")

        yield f

    finally:
        if f is not None:
            f.close()


def put_file(url: str, file: BinaryIO):
    """
    Uploads a file to a given url using multipart upload
    """

    response = requests.put(
        url, data=file, headers={"Content-Type": "application/octet-stream"}
    )
    response.raise_for_status()

    return response
