import logging
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

@dataclass
class Dataset:
    year            : int
    month           : int
    total_sessions  : Optional[int]
    sessions_file   : str
    players_file    : str
    population_file : str

    @property
    def Year(self) -> int:
        return self.year
    @property
    def Month(self) -> int:
        return self.month
    @property
    def TotalSessions(self) -> Optional[int]:
        return self.total_sessions
    @property
    def SessionsFile(self) -> str:
        return self.sessions_file
    @property
    def PlayersFile(self) -> str:
        return self.players_file
    @property
    def PopulationFile(self) -> str:
        return self.population_file
    
    @staticmethod
    def FromDict(raw_dict:Map) -> "Dataset":
        ret_val : Dataset

        expected_keys = {"year", "month", "total_sessions", "sessions_file", "players_file", "population_file"}
        missing_keys = expected_keys - raw_dict.keys()

        if len(missing_keys) == 0:
            ret_val = Dataset(
                year            = raw_dict.get("year", 0),
                month           = raw_dict.get("month", 0),
                total_sessions  = raw_dict.get("total_sessions", None),
                sessions_file   = raw_dict.get("sessions_file", "SESSIONS FILE NOT FOUND"),
                players_file    = raw_dict.get("players_file", "PLAYERS FILE NOT FOUND"),
                population_file = raw_dict.get("population_file", "POPULATION FILE NOT FOUND"),
            )
        else:
            raise KeyError(f"Dataset info source dict had incorrect set of keys, missing {missing_keys}")
        return ret_val

    @staticmethod
    def FromDatasetSchema(schema:DatasetSchema) -> "Dataset":
        return Dataset(
            year=schema.StartDate.year if isinstance(schema.StartDate, date) else int(schema.StartDate.split('-')[0]),
            month=schema.StartDate.month if isinstance(schema.StartDate, date) else int(schema.StartDate.split('-')[1]),
            total_sessions=schema.SessionCount,
            sessions_file=schema.SessionsFile,
            players_file=schema.PlayersFile,
            population_file=schema.PopulationFile
        )

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
