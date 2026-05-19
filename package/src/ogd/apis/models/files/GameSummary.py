import logging
from typing import List, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.enums.ResponseStatus import ResponseStatus
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.utils.typing import Map

class GameSummaryRequest(APIRequest):
    def __init__(self, api_base_url:str, game_id:str, timeout:int=1):
        _url = f"{api_base_url}/games/{game_id}"
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "GameSummaryResponse":
        api_response = super().Execute(logger=logger, retry=retry)
        return GameSummaryResponse.FromAPIResponse(response=api_response)

class GameSummaryResponse(APIResponse):
    def __init__(self, req_type:Optional[RESTType | str], val:Optional[Map], msg:str, status:ResponseStatus):
        if isinstance(val, dict) and not all(key in val.keys() for key in {"game_id", "dataset_count", "session_average", "initial_dataset"}):
            raise ValueError(f"Value map given to GameSummaryResponse had incorrect keys.")
        super().__init__(req_type=req_type, val=val, msg=msg, status=status)

    @property
    def GameID(self) -> str:
        return self.Value.get("game_id", "GAME NOT FOUND") if self.Value else "NO RESPONSE"
    @property
    def DatasetCount(self) -> int:
        return self.Value.get("dataset_count", 0) if self.Value else 0
    @property
    def AverageSessionCount(self) -> Optional[int]:
        return self.Value.get("session_average", None) if self.Value else None
    @property
    def InitialDataset(self) -> str:
        return self.Value.get("initial_dataset", "DATASET NOT FOUND") if self.Value else "NO RESPONSE"

    @staticmethod
    def Default(req_type:RESTType=RESTType.GET):
        return GameSummaryResponse.FromAPIResponse(APIResponse.Default(req_type=req_type))
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "GameSummaryResponse":
        """Set up a GameSummaryResponse from an APIResponse

        This is effectively a copy constructor.

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        return GameSummaryResponse(req_type=response.Type, val=response.Value, msg=response.Message, status=response.Status)

    @staticmethod
    def FromDatasetCollection(game_id:str, dataset_collection:DatasetCollectionSchema):
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
        ret_val = GameSummaryResponse.Default()

        datadates = set(str(dataset.StartDate).replace("/", "-") for dataset in dataset_collection.Datasets.values())
        session_counts=[dataset_collection.Datasets[key].SessionCount for key in sorted(dataset_collection.Datasets.keys(), reverse=True)]
        _val = {
            "game_id"          : game_id,
            "dataset_count"    : len(datadates),
            "average_sessions" : GameSummaryResponse._averageSessions(monthly_session_counts=session_counts),
            "initial_dataset"  : min(datadates)
        }
        ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=_val)

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