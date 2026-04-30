from typing import Final, List

from ogd.apis.models.APIResponse import APIResponse
from ogd.common.utils.typing import Map

class Dataset:
    PATH : Final[str] = "/games/<string:game_id>/datasets/<int:year>"

    def __init__(self, year:int,    month:int,        total_sessions:int,
                 sessions_file:str, players_file:str, population_file:str):
        self._year            = year
        self._month           = month
        self._total_sessions  = total_sessions
        self._sessions_file   = sessions_file
        self._players_file    = players_file
        self._population_file = population_file

    @property
    def Year(self) -> int:
        return self._year
    @property
    def Month(self) -> int:
        return self._month
    @property
    def TotalSessions(self) -> int:
        return self._total_sessions
    @property
    def SessionsFile(self) -> str:
        return self._sessions_file
    @property
    def PlayersFile(self) -> str:
        return self._players_file
    @property
    def PopulationFile(self) -> str:
        return self._population_file

    @property
    def AsDict(self) -> Map:
        return {
            "year": self.Year,
            "month": self.Month,
            "total_sessions": self.TotalSessions,
            "sessions_file": self.SessionsFile,
            "players_file": self.PlayersFile,
            "population_file": self.PopulationFile
        }
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "DatasetsYear":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : DatasetsYear

        if isinstance(response.Value, dict):
            if all(key in response.Value.keys() for key in {"year", "month", "total_sessions", "sessions_file", "players_file", "population_file"}):
                ret_val = DatasetsYear(
                    year=response.Value.get("year", 0),
                    month=response.Value.get("month", 0),
                    total_sessions=response.Value.get("total_sessions", 0),
                    sessions_file=response.Value.get("sessions_file", "SESSIONS FILE NOT FOUND"),
                    players_file=response.Value.get("players_file", "PLAYERS FILE NOT FOUND"),
                    population_file=response.Value.get("population_file", "POPULATION FILE NOT FOUND"),
                )
            else:
                raise ValueError(f"APIResponse for DatasetsYear had incorrect keys.")
        return ret_val