import io
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

try:  # Compatibility with Python 3.7
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


from .base import DatabaseResource
from ..utils import _format_list_response

if TYPE_CHECKING:  # Type hints
    from .dataset import Dataset
    from .dataset_file import File
    import pandas as pd

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
    def name(self) -> str:
        """Name of the version"""
        return self.metadata["name"]

    @property
    def description(self) -> str:
        """Description of the version"""
        return self.metadata["description"]

    @property
    def dataset(self) -> "Dataset":
        """Dataset to which the version belongs"""

        value = self.metadata.get("dataset")
        if value is None or value.get("code") is None:
            return None

        return self._client.get_dataset(value["code"])

    @property
    def files(self) -> List["File"]:
        """List of files associated to the version"""

        files = self.list_files(format="json")
        return [self._client.get_file(file["code"]) for file in files]

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
        params = dict(version=self.code)
        if filetype is not None:
            params["filetype"] = filetype

        # Perform request
        url = self._client._FILE_CLASS._URL
        files = self._client._perform_request(url, params=params).json()

        return _format_list_response(
            files,
            format=format,
            client=self._client,
            cls=self._client._FILE_CLASS,
        )
