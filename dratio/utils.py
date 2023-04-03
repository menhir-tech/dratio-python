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
Utilities for the dratio package.
"""

from typing import Any, Dict, List, Union, Optional

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import pandas as pd


def _format_list_response(
    data: List[Dict[str, Any]],
    format: Literal["pandas", "json", "api"],
    fields: Optional[List[str]] = None,
    client: Optional[Any] = None,
    cls: Optional[Any] = None,
) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
    """Formats a list of dictionaries as a pandas dataframe or a list of
    dictionaries.

    Parameters
    ----------
    data : List[Dict[str, Any]]
        List of dictionaries to format.
    format : Literal['pandas', 'json']
        Format of the output.
    client: Optional[Any]
        Client object used to perform requests to the database.
    cls : Optional[Any]
        Class to use to convert the list of dictionaries to a list of objects.

    Returns
    -------
    Union[pd.DataFrame, List[Dict[str, Any]]]
        List of dictionaries formatted as a pandas dataframe or a list of
        dictionaries.

    Raises
    ------
    ValueError
        If `format` is not 'pandas' or 'json'.
    """
    if cls is None and format == "api":
        raise ValueError(f"format must be 'pandas', 'json', not {format}")

    if format not in ["pandas", "json", "api"]:
        raise ValueError(f"format must be 'pandas', 'json' or 'api', not {format}")

    if format == "pandas":
        data = pd.json_normalize(data)
        # Standardize column names
        data.columns = data.columns.str.replace(".", "_", regex=False)

        if fields is not None:
            data = data[fields]

    if format == "api":
        data = [cls(client=client, code=d.get("code")) for d in data]

    return data


def _remove_and_copy(dictionary: dict, key: str) -> Union[dict, None]:
    """Removes a key from a dictionary and returns a copy of the dictionary
    without the key.

    Parameters
    ----------
    dictionary : dict
        Dictionary from which to remove the key.
    key : str
        Key to remove from the dictionary.

    Returns
    -------
    dict
        Copy of the dictionary without the key.
    """
    if dictionary is None:
        return None

    dictionary = dictionary.copy()
    if key in dictionary:
        del dictionary[key]
    return dictionary
