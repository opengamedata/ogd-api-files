import logging
from dataclasses import dataclass
from typing import List, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.utils.typing import Map

class GameSummaryRequest(APIRequest):
    def __init__(self, api_base_url:str, game_id:str, timeout:int=1):
        _url = f"{api_base_url}/games/{game_id}"
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "GameSummary | APIResponse":
        ret_val : GameSummary | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = GameSummary.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

@dataclass
class GameSummary:
    game_id : str
    dataset_count : int
    average_sessions : Optional[int]
    initial_dataset : str

    @property
    def GameID(self) -> str:
        return self.game_id
    @property
    def DatasetCount(self) -> int:
        return self.dataset_count
    @property
    def AverageSessionCount(self) -> Optional[int]:
        return self.average_sessions
    @property
    def InitialDataset(self) -> str:
        return self.initial_dataset
    
    @staticmethod
    def FromDict(raw_dict:Map) -> "GameSummary":
        """Set up a GameSummaryResponse from an APIResponse

        This is effectively a copy constructor.

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : GameSummary

        expected_keys = {"game_id", "dataset_count", "average_sessions", "initial_dataset"}
        missing_keys = expected_keys - raw_dict.keys()

        if len(missing_keys) == 0:
            ret_val = GameSummary(
                game_id = raw_dict["game_id"],
                dataset_count = raw_dict["dataset_count"],
                average_sessions = raw_dict["average_sessions"],
                initial_dataset = raw_dict["initial_dataset"],
            )
        else:
            raise KeyError(f"GameSummary source dict had incorrect set of keys, missing {missing_keys}")

        return ret_val
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "GameSummary":
        """Set up a GameSummaryResponse from an APIResponse

        This is effectively a copy constructor.

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : GameSummary

        if response.Value is not None:
            ret_val = GameSummary.FromDict(raw_dict=response.Value)
        else:
            raise ValueError(f"Response for GameSummary returned no values!")

        return ret_val

    @staticmethod
    def FromDatasetCollection(game_id:str, dataset_collection:DatasetCollectionSchema) -> "GameSummary":
        """Create a response from a `DatasetCollectionSchema`.

        This will implicitly treat the response as representing a success, given the DatasetCollectionSchema is valid.
        As such, intended for use only by APIs that serve game summaries.

        :param game_id: _description_
        :type game_id: str
        :param dataset_collection: _description_
        :type dataset_collection: DatasetCollectionSchema
        :return: _description_
        :rtype: _type_
        """
        ret_val : GameSummary

        dataset_dates = set(str(dataset.StartDate).replace("/", "-") for dataset in dataset_collection.Datasets.values())
        session_counts=[dataset_collection.Datasets[key].SessionCount for key in sorted(dataset_collection.Datasets.keys(), reverse=True)]

        ret_val = GameSummary(
            game_id = game_id,
            dataset_count = len(dataset_dates),
            average_sessions = GameSummary._averageSessions(monthly_session_counts=session_counts),
            initial_dataset = min(dataset_dates)
        )

        return ret_val

    @staticmethod
    def _averageSessions(monthly_session_counts:List[int | None], month_range:int=12):
        ret_val = 0

        months_counted = 0
        sum_sessions   = 0

        for month in monthly_session_counts:
            # If this month has sessions
            if month is not None and month > 0:
                # Add it to our sum
                sum_sessions += month
            # If we've found a month with sessions either this iteration or a previous iteration
            if sum_sessions > 0:
                # This month counts towards our 12 whether or not it had sessions
                months_counted += 1
            # Once we have 12 months of data we can quit
            if months_counted == month_range:
                break

        # If we counted at least one month
        if months_counted > 0:
            # Return an integer average
            ret_val = (int)(sum_sessions / months_counted)

        return ret_val