import logging
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.utils.typing import Map

class GameListRequest(APIRequest):
    def __init__(self, api_base_url:str, timeout:int=1):
        _url = urljoin(base=api_base_url, url=f"/games")
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "GameList | APIResponse":
        ret_val : GameList | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = GameList.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

@dataclass
class GameList:
    game_ids : List[str]

    def __getitem__(self, index:int):
        return self.GameIDs[index]

    def __setitem__(self, index:int, value):
        self.GameIDs[index] = value

    @property
    def GameIDs(self) -> List[str]:
        return self.game_ids
    
    @staticmethod
    def FromDict(raw_dict:Map) -> "GameList":
        ret_val : GameList

        if "game_ids" in raw_dict.keys():
            ret_val = GameList(game_ids=raw_dict["game_ids"])
        else:
            raise KeyError(f"GameList source dict did not have game_ids element!")

        return ret_val
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "GameList":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : GameList

        if isinstance(response.Value, dict):
            ret_val = GameList.FromDict(response.Value)
        else:
            ret_val = GameList([])
        return ret_val