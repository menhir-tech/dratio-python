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

from typing import Optional


class DratioException(Exception):
    """
    Base class for all dratio exceptions.

    Attributes
    ----------
        message (str): The exception message.

    """


class PermissionDenied(DratioException):
    """
    User does not have permissions to perform the action.

    Attributes
    ----------
        message (str): The exception message.

    """

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = (
                "You do not have permissions to perform this action. "
                "Please contact our support team to upgrade your account."
            )

        super().__init__(message)


class ObjectNotFound(DratioException):
    """
    Object does not exists or does not have visibility permissions.

    Attributes
    ----------
        message (str): The exception message.

    """

    def __init__(self, name: str, code: str = None):
        if code is None:
            message = name
        else:
            message = f"{name} with code {code} not found"
        super().__init__(message)

class InvalidRequest(DratioException):
    """
    Invalid Request
    """