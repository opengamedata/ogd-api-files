from typing import Final, Optional

from ogd.apis.models.APIResponse import APIResponse
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

class DatasetInfo:
    PATH : Final[str] = "/games/<string:game_id>/datasets/<int:year>"

    def __init__(self, first_year:int, first_month:int, last_year:int,     last_month:int,
                       raw_file:Optional[str],   events_file:Optional[str], sessions_file:Optional[str], players_file:Optional[str], population_file:Optional[str],
                       events_template:Optional[str],  sessions_template:Optional[str],  players_template:Optional[str],  population_template:Optional[str],
                       events_codespace:Optional[str], sessions_codespace:Optional[str], players_codespace:Optional[str], population_codespace:Optional[str],
                       detectors_link:Optional[str],   features_link:Optional[str],      found_matching_range:bool):
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
    def RawFile(self) -> Optional[str]:
        return self._raw_file
    @property
    def EventsFile(self) -> Optional[str]:
        return self._events_file
    @property
    def SessionsFile(self) -> Optional[str]:
        return self._sessions_file
    @property
    def PlayersFile(self) -> Optional[str]:
        return self._players_file
    @property
    def PopulationFile(self) -> Optional[str]:
        return self._population_file
    @property
    def EventsTemplate(self) -> Optional[str]:
        return self._events_template
    @property
    def SessionsTemplate(self) -> Optional[str]:
        return self._sessions_template
    @property
    def PlayersTemplate(self) -> Optional[str]:
        return self._players_template
    @property
    def PopulationTemplate(self) -> Optional[str]:
        return self._population_template
    @property
    def EventsCodespace(self) -> Optional[str]:
        return self._events_codespace
    @property
    def SessionsCodespace(self) -> Optional[str]:
        return self._sessions_codespace
    @property
    def PlayersCodespace(self) -> Optional[str]:
        return self._players_codespace
    @property
    def PopulationCodespace(self) -> Optional[str]:
        return self._population_codespace
    @property
    def DetectorsLink(self) -> Optional[str]:
        return self._detectors_link
    @property
    def FeaturesLink(self) -> Optional[str]:
        return self._features_link

    @property
    def AsDict(self) -> Map:
        return {
            "first_year": self.FirstYear,
            "first_month": self.FirstMonth,
            "last_year": self.LastYear,
            "last_month": self.LastMonth,
            "raw_file": self.RawFile,
            "events_file": self.EventsFile,
            "sessions_file": self.SessionsFile,
            "players_file": self.PlayersFile,
            "population_file": self.PopulationFile,
            "events_template": self.EventsTemplate,
            "sessions_template": self.SessionsTemplate,
            "players_template": self.PlayersTemplate,
            "population_template": self.PopulationTemplate,
            "events_codespace": self.EventsCodespace,
            "sessions_codespace": self.SessionsCodespace,
            "players_codespace": self.PlayersCodespace,
            "population_codespace": self.PopulationCodespace,
            "detectors_link": self.DetectorsLink,
            "features_link": self.FeaturesLink,
            "found_matching_range": self._found_matching_range
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
            expected_keys = {
                "first_year", "first_month", "last_year", "last_month",
                "raw_file", "events_file", "sessions_file", "players_file", "population_file",
                "events_template", "sessions_template", "players_template", "population_template",
                "events_codespace", "sessions_codespace", "players_codespace", "population_codespace",
                "detectors_link", "features_link", "found_matching_range"
            }
            if all(key in response.Value.keys() for key in expected_keys):
                ret_val = DatasetInfo(
                    first_year=response.Value.get("first_year", 0),
                    first_month=response.Value.get("first_month", 0),
                    last_year=response.Value.get("last_year", 0),
                    last_month=response.Value.get("last_month", 0),
                    raw_file=response.Value.get("raw_file"),
                    events_file=response.Value.get("events_file"),
                    sessions_file=response.Value.get("sessions_file"),
                    players_file=response.Value.get("players_file"),
                    population_file=response.Value.get("population_file"),
                    events_template=response.Value.get("events_template"),
                    sessions_template=response.Value.get("sessions_template"),
                    players_template=response.Value.get("players_template"),
                    population_template=response.Value.get("population_template"),
                    events_codespace=response.Value.get("events_codespace"),
                    sessions_codespace=response.Value.get("sessions_codespace"),
                    players_codespace=response.Value.get("players_codespace"),
                    population_codespace=response.Value.get("population_codespace"),
                    detectors_link=response.Value.get("detectors_link"),
                    features_link=response.Value.get("features_link"),
                    found_matching_range=response.Value.get("found_matching_range", False)
                )
            else:
                raise ValueError(f"APIResponse for DatasetInfo had incorrect keys.")
        return ret_val