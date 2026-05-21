import logging
from dataclasses import dataclass
from typing import Final, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

class DatasetSummaryRequest(APIRequest):
    def __init__(self, api_base_url:str, game_id:str, year:int, month:int, timeout:int=1):
        _url = f"{api_base_url}/games/{game_id}/datasets/{year}/{month}"
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "DatasetSummary | APIResponse":
        ret_val : DatasetSummary | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = DatasetSummary.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

@dataclass
class DatasetSummary:
    first_year           : int
    first_month          : int
    last_year            : int
    last_month           : int
    raw_file             : Optional[str]
    events_file          : Optional[str]
    sessions_file        : Optional[str]
    players_file         : Optional[str]
    population_file      : Optional[str]
    events_template      : Optional[str]
    sessions_template    : Optional[str]
    players_template     : Optional[str]
    population_template  : Optional[str]
    events_codespace     : Optional[str]
    sessions_codespace   : Optional[str]
    players_codespace    : Optional[str]
    population_codespace : Optional[str]
    detectors_link       : Optional[str]
    features_link        : Optional[str]
    found_matching_range : bool

    @property
    def FirstYear(self) -> int:
        return self.first_year
    @property
    def FirstMonth(self) -> int:
        return self.first_month
    @property
    def LastYear(self) -> int:
        return self.last_year
    @property
    def LastMonth(self) -> int:
        return self.last_month
    @property
    def RawFile(self) -> Optional[str]:
        return self.raw_file
    @property
    def EventsFile(self) -> Optional[str]:
        return self.events_file
    @property
    def SessionsFile(self) -> Optional[str]:
        return self.sessions_file
    @property
    def PlayersFile(self) -> Optional[str]:
        return self.players_file
    @property
    def PopulationFile(self) -> Optional[str]:
        return self.population_file
    @property
    def EventsTemplate(self) -> Optional[str]:
        return self.events_template
    @property
    def SessionsTemplate(self) -> Optional[str]:
        return self.sessions_template
    @property
    def PlayersTemplate(self) -> Optional[str]:
        return self.players_template
    @property
    def PopulationTemplate(self) -> Optional[str]:
        return self.population_template
    @property
    def EventsCodespace(self) -> Optional[str]:
        return self.events_codespace
    @property
    def SessionsCodespace(self) -> Optional[str]:
        return self.sessions_codespace
    @property
    def PlayersCodespace(self) -> Optional[str]:
        return self.players_codespace
    @property
    def PopulationCodespace(self) -> Optional[str]:
        return self.population_codespace
    @property
    def DetectorsLink(self) -> Optional[str]:
        return self.detectors_link
    @property
    def FeaturesLink(self) -> Optional[str]:
        return self.features_link

    @staticmethod
    def FromDict(raw_dict:Map) -> "DatasetSummary":
        ret_val : DatasetSummary

        expected_keys = {
            "first_year", "first_month", "last_year", "last_month",
            "raw_file", "events_file", "sessions_file", "players_file", "population_file",
            "events_template", "sessions_template", "players_template", "population_template",
            "events_codespace", "sessions_codespace", "players_codespace", "population_codespace",
            "detectors_link", "features_link", "found_matching_range"
        }
        missing_keys = expected_keys - raw_dict.keys()
        if len(missing_keys) == 0:
            ret_val = DatasetSummary(
                first_year           = raw_dict.get("first_year", 0),
                first_month          = raw_dict.get("first_month", 0),
                last_year            = raw_dict.get("last_year", 0),
                last_month           = raw_dict.get("last_month", 0),
                raw_file             = raw_dict.get("raw_file"),
                events_file          = raw_dict.get("events_file"),
                sessions_file        = raw_dict.get("sessions_file"),
                players_file         = raw_dict.get("players_file"),
                population_file      = raw_dict.get("population_file"),
                events_template      = raw_dict.get("events_template"),
                sessions_template    = raw_dict.get("sessions_template"),
                players_template     = raw_dict.get("players_template"),
                population_template  = raw_dict.get("population_template"),
                events_codespace     = raw_dict.get("events_codespace"),
                sessions_codespace   = raw_dict.get("sessions_codespace"),
                players_codespace    = raw_dict.get("players_codespace"),
                population_codespace = raw_dict.get("population_codespace"),
                detectors_link       = raw_dict.get("detectors_link"),
                features_link        = raw_dict.get("features_link"),
                found_matching_range = raw_dict.get("found_matching_range", False)
            )
        else:
            raise KeyError(f"DatasetSummary source dict had incorrect set of keys, missing {missing_keys}")

        return ret_val

    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "DatasetSummary":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : DatasetSummary

        if response.Value is not None:
            ret_val = DatasetSummary.FromDict(raw_dict=response.Value)
        else:
            raise ValueError(f"Response for DataSummary returned no values!")

        return ret_val