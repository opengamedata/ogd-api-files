import logging
from dataclasses import dataclass
from typing import Final, List, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.files.Dataset import Dataset
from ogd.common.utils.typing import Map

class DatasetListRequest(APIRequest):
    def __init__(self, api_base_url:str, game_id:str, year:Optional[int]=None, timeout:int=1):
        _year_component = f"/{year}" if year is not None else ""
        _url = f"{api_base_url}/games/{game_id}/datasets{_year_component}"
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "DatasetList | APIResponse":
        ret_val : DatasetList | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = DatasetList.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

@dataclass
class DatasetList:
    datasets : List[Dataset]

    def __getitem__(self, index:int):
        return self.Datasets[index]

    def __setitem__(self, index:int, value):
        self.Datasets[index] = value

    @property
    def Datasets(self) -> List[Dataset]:
        return self.datasets
    
    @staticmethod
    def FromDict(raw_dict:Map) -> "DatasetList":
        ret_val : DatasetList

        if "datasets" in raw_dict.keys():
            ret_val = DatasetList(datasets=[Dataset.FromDict(dataset) for dataset in raw_dict["datasets"]])
        else:
            raise KeyError(f"DatasetList source dict did not have datasets element!")

        return ret_val
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "DatasetList":
        """Parse a DatasetList from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : DatasetList

        if isinstance(response.Value, dict):
            ret_val = DatasetList.FromDict(response.Value)
        else:
            ret_val = DatasetList([])
        return ret_val