import logging
from typing import Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

class DatasetResourcesRequest(APIRequest):
    def __init__(self, api_base_url:URLLocationConfig | str, game_id:str, year:int, month:int, timeout:int=1):
        url : URLLocationConfig
        match api_base_url:
            case URLLocationConfig():
                url = api_base_url
            case str():
                url = URLLocationConfig.FromString(name="API Location", raw_url=api_base_url)
        endpoint = URLLocationConfig.FromString(name="Endpoint", raw_url=f"/games/{game_id}/datasets/{year}/{month}")
        super().__init__(url=url + endpoint, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "DatasetResources | APIResponse":
        ret_val : DatasetResources | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = DatasetResources.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

class DatasetResources(DatasetSchema):
    def __init__(self, dataset_schema:DatasetSchema,
                 events_template:Optional[str],  sessions_template:Optional[str],  players_template:Optional[str],  population_template:Optional[str],
                 events_codespace:Optional[str], sessions_codespace:Optional[str], players_codespace:Optional[str], population_codespace:Optional[str],
                 detectors_link:Optional[str],   features_link:Optional[str]):
        self._dataset_schema : DatasetSchema = dataset_schema
        super().__init__(
            name=dataset_schema.Name,
            game_id=dataset_schema._key.GameID,
            dataset_id=None,
            filters=dataset_schema.Filters,
            session_ct=dataset_schema.SessionCount,
            player_ct=dataset_schema.PlayerCount,
            game_state=dataset_schema.GameState,
            events=dataset_schema.Events,
            features=dataset_schema.Features,
            event_spec_version=dataset_schema.EventSpecificationVersion,
            ogd_version=dataset_schema.OGDVersion,
            ogd_revision=dataset_schema.OGDRevision,
            base_files_location=dataset_schema.BaseFileLocation,
            all_events_file=dataset_schema._all_events_file,
            game_events_file=dataset_schema._game_events_file,
            combined_feats_file=dataset_schema._all_features_file,
            sessions_file=dataset_schema._sessions_file,
            players_file=dataset_schema._players_file,
            population_file=dataset_schema._population_file,
            start_date=dataset_schema.StartDate,
            end_date=dataset_schema.EndDate,
            date_modified=dataset_schema.DateModified
        )
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
            "start_date" : self.StartDate.strftime("%m/%d/%Y") if self.StartDate else None,
            "end_date" : self.EndDate.strftime("%m/%d/%Y") if self.EndDate else None,
            "game_events_file" : self.GameEventsFile(relative=False),
            "all_events_file" : self.AllEventsFile(relative=False),
            "sessions_file" : self.SessionsFile(relative=False),
            "players_file" : self.PlayersFile(relative=False),
            "population_file" : self.PopulationFile(relative=False),
            "combined_features_file" : self.CombinedFeaturesFile(relative=False),
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
            events_template=f"{template_url_base}/tree/{_branch_name}"     if dataset_schema.AllEventsFile() or dataset_schema.GameEventsFile() else None,
            sessions_template=f"{template_url_base}/tree/{_branch_name}"   if dataset_schema.SessionsFile()   else None,
            players_template=f"{template_url_base}/tree/{_branch_name}"    if dataset_schema.PlayersFile()    else None,
            population_template=f"{template_url_base}/tree/{_branch_name}" if dataset_schema.PopulationFile() else None,
            events_codespace=f"{codespace_tree_url}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json"        if dataset_schema.AllEventsFile() or dataset_schema.GameEventsFile() else None,
            sessions_codespace=f"{codespace_tree_url}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%session-template%2Fdevcontainer.json"      if dataset_schema.SessionsFile()   else None,
            players_codespace=f"{codespace_tree_url}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%player-template%2Fdevcontainer.json"        if dataset_schema.PlayersFile()    else None,
            population_codespace=f"{codespace_tree_url}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%population-template%2Fdevcontainer.json" if dataset_schema.PopulationFile() else None,
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
            raise ValueError(f"Response for DataSummary contained no values!")

        return ret_val