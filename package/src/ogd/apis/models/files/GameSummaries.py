import dataclasses
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.files.GameSummary import GameSummary
from ogd.common.utils.typing import Map

class GameSummariesRequest(APIRequest):
    def __init__(self, api_base_url:str, timeout:int=1):
        _url = urljoin(base=api_base_url, url=f"/games/details")
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "GameSummaries | APIResponse":
        ret_val : GameSummaries | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = GameSummaries.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

class GameSummaries:
    def __init__(self, summaries:Dict[str, GameSummary]) -> None:
        self._summaries = summaries

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
        return self._summaries

    @property
    def AsDict(self) -> Map:
        return {key : dataclasses.asdict(val) for key,val in self.items()}
    
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
        self._summaries[summary.GameID] = summary