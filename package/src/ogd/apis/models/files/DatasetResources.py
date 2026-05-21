import logging
from datetime import date
from pathlib import Path
from typing import Final, Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

class DatasetResourcesRequest(APIRequest):
    def __init__(self, api_base_url:str, game_id:str, year:int, month:int, timeout:int=1):
        _url = f"{api_base_url}/games/{game_id}/datasets/{year}/{month}"
        super().__init__(url=_url, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "DatasetResources | APIResponse":
        ret_val : DatasetResources | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = DatasetResources.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

class DatasetResources:
    def __init__(self, dataset_schema:DatasetSchema,
                 events_template:Optional[str],  sessions_template:Optional[str],  players_template:Optional[str],  population_template:Optional[str],
                 events_codespace:Optional[str], sessions_codespace:Optional[str], players_codespace:Optional[str], population_codespace:Optional[str],
                 detectors_link:Optional[str],   features_link:Optional[str]):
        self._dataset_schema : DatasetSchema = dataset_schema
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

    @property
    def StartDate(self) -> date | str:
        return self._dataset_schema.StartDate
    @property
    def EndDate(self) -> date | str:
        return self._dataset_schema.EndDate
    @property
    def GameEventsFile(self) -> Optional[Path]:
        return self._dataset_schema.GameEventsFile
    @property
    def AllEventsFile(self) -> Optional[Path]:
        return self._dataset_schema.AllEventsFile
    @property
    def SessionsFile(self) -> Optional[Path]:
        return self._dataset_schema.SessionsFile
    @property
    def PlayersFile(self) -> Optional[Path]:
        return self._dataset_schema.PlayersFile
    @property
    def PopulationFile(self) -> Optional[Path]:
        return self._dataset_schema.PopulationFile
    @property
    def CombinedFeaturesFile(self) -> Optional[Path]:
        return self._dataset_schema.CombinedFeaturesFile
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
        return self._dataset_schema.AsDict | {
            "start_date" : str(self.StartDate),
            "end_date" : str(self.EndDate),
            "game_events_file" : str(self.GameEventsFile) if self.GameEventsFile else None,
            "all_events_file" : str(self.AllEventsFile) if self.AllEventsFile else None,
            "sessions_file" : str(self.SessionsFile) if self.SessionsFile else None,
            "players_file" : str(self.PlayersFile) if self.PlayersFile else None,
            "population_file" : str(self.PopulationFile) if self.PopulationFile else None,
            "combined_features_file" : str(self.CombinedFeaturesFile) if self.CombinedFeaturesFile else None,
            "events_template" : self.EventsTemplate,
            "sessions_template" : self.SessionsTemplate,
            "players_template" : self.PlayersTemplate,
            "population_template" : self.PopulationTemplate,
            "events_codespace" : self.EventsCodespace,
            "sessions_codespace" : self.SessionsCodespace,
            "players_codespace" : self.PlayersCodespace,
            "population_codespace" : self.PopulationCodespace,
            "detectors_link" : self.DetectorsLink,
            "features_link" : self.FeaturesLink
        }

    @staticmethod
    def FromBaseURLs(dataset_schema:DatasetSchema,
                     game_id:str,
                     template_url_base:str,
                     codespace_tree_url:str,
                     github_tree_url:str) -> "DatasetResources":
        """Generate a DatasetSummary by providing base URLs for the templates,
        codespaces, and github, rather than full URLs for every datset-related link.

        :param dataset_schema: _description_
        :type dataset_schema: DatasetSchema
        :param game_id: _description_
        :type game_id: str
        :param template_url_base: _description_
        :type template_url_base: str
        :param codespace_tree_url: _description_
        :type codespace_tree_url: str
        :param github_tree_url: _description_
        :type github_tree_url: str
        :return: _description_
        :rtype: DatasetSummary
        """
        codespace_tree_url = f"{codespace_tree_url}/" if not codespace_tree_url.endswith("/") else codespace_tree_url
        github_tree_url    = f"{github_tree_url}/" if not github_tree_url.endswith("/") else github_tree_url
        _branch_name       = game_id.lower().replace('_', '-')
        return DatasetResources(
            dataset_schema=dataset_schema,
            events_template=f"{template_url_base}/tree/{_branch_name}",
            sessions_template=f"{template_url_base}/tree/{_branch_name}",
            players_template=f"{template_url_base}/tree/{_branch_name}",
            population_template=f"{template_url_base}/tree/{_branch_name}",
            events_codespace=f"{codespace_tree_url}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json",
            sessions_codespace=f"{codespace_tree_url}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%session-template%2Fdevcontainer.json",
            players_codespace=f"{codespace_tree_url}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%player-template%2Fdevcontainer.json",
            population_codespace=f"{codespace_tree_url}?quickstart=1&devcontainer_path=.devcontainer%population-template%2Fdevcontainer.json",
            features_link=f"{github_tree_url}{dataset_schema.OGDRevision}/src/ogd/games/{game_id}/detectors" if dataset_schema.OGDRevision else None,
            detectors_link=f"{github_tree_url}{dataset_schema.OGDRevision}/src/ogd/games/{game_id}/detectors" if dataset_schema.OGDRevision else None,
        )

    @staticmethod
    def FromDict(raw_dict:Map) -> "DatasetResources":
        ret_val : DatasetResources

        expected_keys = {
            "first_year", "first_month", "last_year", "last_month",
            "game_events_file", "all_events_file",
            "sessions_file", "players_file", "population_file", "combined_features_file",
            "events_template", "sessions_template", "players_template", "population_template",
            "events_codespace", "sessions_codespace", "players_codespace", "population_codespace",
            "detectors_link", "features_link"
        }
        missing_keys = expected_keys - raw_dict.keys()
        if len(missing_keys) == 0:
            schema = DatasetSchema.FromDict(name="DatasetSchema", unparsed_elements=raw_dict)
            ret_val = DatasetResources(
                dataset_schema=schema,
                events_template      = raw_dict.get("events_template"),
                sessions_template    = raw_dict.get("sessions_template"),
                players_template     = raw_dict.get("players_template"),
                population_template  = raw_dict.get("population_template"),
                events_codespace     = raw_dict.get("events_codespace"),
                sessions_codespace   = raw_dict.get("sessions_codespace"),
                players_codespace    = raw_dict.get("players_codespace"),
                population_codespace = raw_dict.get("population_codespace"),
                detectors_link       = raw_dict.get("detectors_link"),
                features_link        = raw_dict.get("features_link")
            )
        else:
            raise KeyError(f"DatasetSummary source dict had incorrect set of keys, missing {missing_keys}")

        return ret_val

    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "DatasetResources":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : DatasetResources

        if response.Value is not None:
            ret_val = DatasetResources.FromDict(raw_dict=response.Value)
        else:
            raise ValueError(f"Response for DataSummary returned no values!")

        return ret_val