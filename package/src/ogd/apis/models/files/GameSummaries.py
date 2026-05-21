import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.files.GameSummary import GameSummary

class GameSummariesRequest(APIRequest):
    def __init__(self, api_base_url:str, timeout:int=1):
        _url = f"{api_base_url}/games/details"
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "GameSummaries | APIResponse":
        ret_val : GameSummaries | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = GameSummaries.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

@dataclass
class GameSummaries:
    summaries : Dict[str, GameSummary]

    def __getitem__(self, key):
        return self.Summaries[key]

    def __setitem__(self, key, value):
        self.Summaries[key] = value

    def get(self, key:str, default:Any=None):
        return self.Summaries.get(key, default)

    def items(self):
        return self.Summaries.items()

    def keys(self):
        return self.Summaries.keys()

    def values(self):
        return self.Summaries.values()

    @property
    def Summaries(self) -> Dict[str, GameSummary]:
        return self.summaries
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "GameSummaries":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : GameSummaries

        if response.Value is not None:
            ret_val = GameSummaries(summaries=response.Value)
        else:
            ret_val = GameSummaries({})
        return ret_val


    def insert(self, summary:GameSummary):
        self.summaries[summary.GameID] = summary