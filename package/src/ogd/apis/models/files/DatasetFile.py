from typing import Final, List

from ogd.apis.models.APIResponse import APIResponse
from ogd.common.utils.typing import Map

class DatasetFile:
    PATH : Final[str] = "/games/<string:game_id>/datasets/<int:year>"

    def __init__(self, columns:List,    rows:List):
        self._columns = columns
        self._rows    = rows

    @property
    def Columns(self) -> List:
        return self._columns
    @property
    def Rows(self) -> List:
        return self._rows

    @property
    def AsDict(self) -> Map:
        return {
            "columns": self.Columns,
            "rows": self.Rows
        }
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "DatasetFile":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : DatasetFile

        if isinstance(response.Value, dict):
            if all(key in response.Value.keys() for key in {"columns", "rows"}):
                ret_val = DatasetFile(
                    columns=response.Value.get("columns", ["NO COLUMNS FOUND"]),
                    rows=response.Value.get("rows", ["NO ROWS FOUND"]),
                )
            else:
                raise ValueError(f"APIResponse for DatasetFile had incorrect keys.")
        return ret_val