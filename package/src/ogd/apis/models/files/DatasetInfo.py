from typing import Final, List

from ogd.apis.models.APIResponse import APIResponse
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

class DatasetInfo:
    PATH : Final[str] = "/games/<string:game_id>/datasets/<int:year>"

    def __init__(self, first_year:int, first_month:int, last_year:int,     last_month:int,
                       raw_file:str,   events_file:str, sessions_file:str, players_file:str, population_file:str,
                       events_template:str,  sessions_template:str,  players_template:str,  population_template:str,
                       events_codespace:str, sessions_codespace:str, players_codespace:str, population_codespace:str,
                       detectors_link:str,   features_link:str,      found_matching_range:bool):
        self._first_year      = first_year
        self._first_month     = first_month
        self._last_year       = last_year
        self._last_month      = last_month
        self._raw_file        = raw_file
        self._events_file     = events_file
        self._sessions_file   = sessions_file
        self._players_file    = players_file
        self._population_file = population_file
        self._events_template      = events_template
        self._sessions_template    = sessions_template
        self._players_template     = players_template
        self._population_template  = population_template
        self._events_codespace     = events_codespace
        self._sessions_codespace   = sessions_codespace
        self._players_codespace    = players_codespace
        self._population_codespace = population_codespace
        self._detectors_link       = detectors_link
        self._features_link        = features_link
        self._found_matching_range = found_matching_range

    @property
    def FirstYear(self) -> int:
        return self._first_year
    @property
    def FirstMonth(self) -> int:
        return self._first_month
    @property
    def LastYear(self) -> int:
        return self._last_year
    @property
    def LastMonth(self) -> int:
        return self._last_month
    @property
    def RawFile(self) -> str:
        return self._raw_file
    @property
    def EventsFile(self) -> str:
        return self._events_file
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
    def EventsTemplate(self) -> str:
        return self._events_template
    @property
    def SessionsTemplate(self) -> str:
        return self._sessions_template
    @property
    def PlayersTemplate(self) -> str:
        return self._players_template
    @property
    def PopulationTemplate(self) -> str:
        return self._population_template
    @property
    def EventsCodespace(self) -> str:
        return self._events_codespace
    @property
    def SessionsCodespace(self) -> str:
        return self._sessions_codespace
    @property
    def PlayersCodespace(self) -> str:
        return self._players_codespace
    @property
    def PopulationCodespace(self) -> str:
        return self._population_codespace

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
    def FromAPIResponse(response:APIResponse) -> "DatasetInfo":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : DatasetInfo

        if isinstance(response.Value, dict):
            if all(key in response.Value.keys() for key in {"year", "month", "total_sessions", "sessions_file", "players_file", "population_file"}):
                ret_val = DatasetInfo(
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