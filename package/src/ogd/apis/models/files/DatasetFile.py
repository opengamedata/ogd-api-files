import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.utils.typing import Map

class FileTypes(Enum):
    """Enum type representing the file types currently supported by the DatasetFile endpoint.

    In particular, this endpoint can be used to retrieve any of the three granular feature file types:
    sessions, players, and population.

    Event data and the "combined" feature format are not yet supported.
    """
    SESSION = 1
    PLAYER = 2
    POPULATION = 3

    def __str__(self):
        return self.name

class DatasetFileRequest(APIRequest):
    def __init__(self, api_base_url:str, game_id:str, year:int, month:int, file_type:FileTypes | str, timeout:int=1):
        _url = f"{api_base_url}/games/{game_id}/datasets/{year}/{month}/{file_type}"
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "DatasetFile | APIResponse":
        ret_val : DatasetFile | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = DatasetFile.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

@dataclass
class DatasetFile:
    columns : List[str]
    rows    : List[Any]

    @property
    def Columns(self) -> List[str]:
        return self.columns
    @property
    def Rows(self) -> List[Any]:
        return self.rows

    @staticmethod
    def FromDict(raw_dict:Map) -> "DatasetFile":
        ret_val : DatasetFile

        expected_keys = {"columns", "rows"}
        missing_keys = expected_keys - raw_dict.keys()

        if len(missing_keys) == 0:
            ret_val = DatasetFile(
                columns = raw_dict["columns"],
                rows    = raw_dict["rows"]
            )
        else:
            raise KeyError(f"DatasetFile source dict had incorrect set of keys, missing {missing_keys}")

        return ret_val

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
            ret_val = DatasetFile.FromDict(raw_dict=response.Value)
        else:
            raise ValueError(f"Response for DatasetFile contained no values!")
        return ret_val