from typing import Final, Optional
from ogd.apis.models.APIResponse import APIResponse
from ogd.common.utils.typing import Map

class GameSummary:
    PATH : Final[str] = "/games/<string:game_id>"

    def __init__(self, game_id:str, dataset_count:int, session_avg:Optional[int], initial_dataset:str):
        self._game_id = game_id
        self._dataset_count = dataset_count
        self._session_avg   = session_avg
        self._initial_dataset = initial_dataset

    @property
    def GameID(self) -> str:
        return self._game_id
    @property
    def DatasetCount(self) -> int:
        return self._dataset_count
    @property
    def SessionAverage(self) -> Optional[int]:
        return self._session_avg
    @property
    def InitialDataset(self) -> str:
        return self._initial_dataset

    @property
    def AsDict(self) -> Map:
        return {
            "game_id": self.GameID,
            "dataset_count": self.DatasetCount,
            "session_average": self.SessionAverage,
            "initial_dataset": self.InitialDataset
        }
    
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
                    session_avg=response.Value.get("session_average", None),
                    initial_dataset=response.Value.get("initial_dataset", "DATASET NOT FOUND")
                )
            else:
                raise ValueError(f"APIResponse for GameSummary had incorrect keys.")
        return ret_val