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
This module contains the tags classes. A Category is a tag that describes the
nature of the data. A Scope is a tag that describes the geographical scope of
the data. A Unit is a tag that describes the unit of measurement of the data.
"""

from .base import DatabaseResource


__all__ = ["Category", "Scope", "Unit"]


class Category(DatabaseResource):
    """
    Class to represent a category in the database.

    A category is a tag that describes the nature of the data.
    """

    _URL = "category/"
    _LIST_FIELDS = ["code", "name"]


class Scope(DatabaseResource):
    """
    Class to represent a scope in the database.

    A scope is a tag that describes the geographical scope of the data.
    """

    _URL = "scope/"
    _LIST_FIELDS = ["code", "name"]


class Unit(DatabaseResource):
    """
    Class to represent a unit in the database.

    A unit is a tag that describes the unit of measurement of the data.
    """

    _URL = "unit/"
    _LIST_FIELDS = ["code", "name", "symbol"]

class PusblisherType(DatabaseResource):
    """
    Class to represent a unit in the database.

    A unit is a tag that describes the unit of measurement of the data.
    """

    _URL = "publisher-type/"
    _LIST_FIELDS = ["code", "name"]


class DataLevel(DatabaseResource):
    """
    Class to represent a unit in the database.

    A unit is a tag that describes the unit of measurement of the data.
    """

    _URL = "unit/"
    _LIST_FIELDS = ["code", "name", "symbol"]
