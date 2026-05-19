from typing import Dict, Final, List

from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.files.GameSummary import GameSummary
from ogd.common.utils.typing import Map

class GameSummaries:
    PATH : Final[str] = "/games/<str:game_id>"

    def __init__(self, game_summaries:Dict[str, GameSummary]):
        self._summaries = game_summaries

    @property
    def Summaries(self) -> Dict[str, GameSummary]:
        return self._summaries

    @property
    def AsDict(self) -> Map:
        return {
            key: val.AsDict for key,val in self.Summaries.items()
        }
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "GameSummaries":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : GameList

        if isinstance(response.Value, dict):
            if all(key in response.Value.keys() for key in {"game_ids"}):
                ret_val = GameList(
                    game_ids=response.Value.get("game_ids", "GAMES NOT FOUND"),
                )
            else:
                raise ValueError(f"APIResponse for GamesList had incorrect keys.")
        return ret_val