from typing import Final, List, Optional
from ogd.apis.models.APIResponse import APIResponse
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.utils.typing import Map

class GameSummary:
    PATH : Final[str] = "/games/<string:game_id>"

    def __init__(self, game_id:str, dataset_count:int, average_sessions:Optional[int], initial_dataset:str):
        self._game_id = game_id
        self._dataset_count = dataset_count
        self._avg_sessions   = average_sessions
        self._initial_dataset = initial_dataset

    @property
    def GameID(self) -> str:
        return self._game_id
    @property
    def DatasetCount(self) -> int:
        return self._dataset_count
    @property
    def AverageSessionCount(self) -> Optional[int]:
        return self._avg_sessions
    @property
    def InitialDataset(self) -> str:
        return self._initial_dataset

    @property
    def AsDict(self) -> Map:
        return {
            "game_id": self.GameID,
            "dataset_count": self.DatasetCount,
            "session_average": self.AverageSessionCount,
            "initial_dataset": self.InitialDataset
        }

    @staticmethod
    def FromDatasetCollection(game_id:str, dataset_collection:DatasetCollectionSchema):
        datadates = set(str(dataset.StartDate).replace("/", "-") for dataset in dataset_collection.Datasets.values())
        return GameSummary(
            game_id          = game_id,
            dataset_count    = len(datadates),
            average_sessions  = GameSummary._averageSessions(monthly_session_counts=session_counts),
            initial_dataset  = min(datadates)
        )
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "GameSummary":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : GameSummary

        if isinstance(response.Value, dict):
            if all(key in response.Value.keys() for key in {"game_id", "dataset_count", "session_average", "initial_dataset"}):
                ret_val = GameSummary(
                    game_id=response.Value.get("game_id", "GAME NOT FOUND"),
                    dataset_count=response.Value.get("dataset_count", 0),
                    average_sessions=response.Value.get("session_average", None),
                    initial_dataset=response.Value.get("initial_dataset", "DATASET NOT FOUND")
                )
            else:
                raise ValueError(f"APIResponse for GameSummary had incorrect keys.")
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