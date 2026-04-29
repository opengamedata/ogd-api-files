from typing import List

from ogd.apis.models.APIResponse import APIResponse
from ogd.common.utils.typing import Map

class GameList:
    def __init__(self, game_ids:List[str]):
        self._game_ids = game_ids

    @property
    def GameIDs(self) -> List[str]:
        return self._game_ids

    @property
    def AsDict(self) -> Map:
        return {
            "game_ids": self.GameIDs
        }
    
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
            if all(key in response.Value.keys() for key in {"game_ids"}):
                ret_val = GameList(
                    game_ids=response.Value.get("game_ids", "GAMES NOT FOUND"),
                )
            else:
                raise ValueError(f"APIResponse for GamesList had incorrect keys.")
        return ret_val