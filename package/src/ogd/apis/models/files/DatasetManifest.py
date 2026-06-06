import logging
from typing import Optional

from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import JSONMap, Map

class DatasetManifestRequest(APIRequest):
    def __init__(self, api_base_url:URLLocationConfig | str, game_id:str, year:int, month:int, timeout:int=1):
        url : URLLocationConfig
        match api_base_url:
            case URLLocationConfig():
                url = api_base_url
            case str():
                url = URLLocationConfig.FromString(name="API Location", raw_url=api_base_url)
        endpoint = URLLocationConfig.FromString(name="Endpoint", raw_url=f"/games/{game_id}/datasets/{year}/{month}/manifest")
        super().__init__(url=url + endpoint, request_type=RESTType.GET, params=None, body=None, timeout=timeout)

    def Execute(self, logger:Optional[logging.Logger]=None, retry:int=0) -> "DatasetManifest | APIResponse":
        ret_val : DatasetManifest | APIResponse

        api_response = super().Execute(logger=logger, retry=retry)
        try:
            ret_val = DatasetManifest.FromAPIResponse(response=api_response)
        except (ValueError, KeyError):
            ret_val = api_response

        return ret_val

class DatasetManifest(DatasetSchema):
    def __init__(self, dataset_schema:DatasetSchema):
        super().__init__(
            name=dataset_schema.Name,
            game_id=None,
            dataset_id=dataset_schema.Key,
            filters=dataset_schema.Filters,
            session_ct=dataset_schema.SessionCount,
            player_ct=dataset_schema.PlayerCount,
            game_state=dataset_schema.GameState,
            events=dataset_schema.Events,
            features=dataset_schema.Features,
            ogd_version=dataset_schema.OGDVersion,
            ogd_revision=dataset_schema.OGDRevision,
            event_spec_version=dataset_schema.EventSpecificationVersion,
            base_files_location=dataset_schema._base_files_location,
            all_events_file=dataset_schema._all_events_file,
            game_events_file=dataset_schema._game_events_file,
            sessions_file=dataset_schema._sessions_file,
            players_file=dataset_schema._players_file,
            population_file=dataset_schema._population_file,
            combined_feats_file=dataset_schema._all_features_file,
            start_date=dataset_schema.StartDate,
            end_date=dataset_schema.EndDate,
            date_modified=dataset_schema.DateModified,
        )

    @staticmethod
    def FromDict(raw_dict:Map) -> "DatasetManifest":
        ret_val : DatasetManifest

        schema = DatasetSchema.FromDict(name="DatasetSchema", unparsed_elements=raw_dict)
        ret_val = DatasetManifest(dataset_schema=schema)

        return ret_val

    @property
    def AsDict(self) -> JSONMap:
        overrides : JSONMap = {
            "output": {
                "all_events_file"    : self.AllEventsFile(relative=False),
                "game_events_file"   : self.GameEventsFile(relative=False),
                "all_features_file"  : self.CombinedFeaturesFile(relative=False),
                "sessions_file"      : self.SessionsFile(relative=False),
                "players_file"       : self.PlayersFile(relative=False),
                "population_file"    : self.PopulationFile(relative=False)
            }
        }
        return super().AsDict | overrides
    
    @staticmethod
    def FromAPIResponse(response:APIResponse) -> "DatasetManifest":
        """Parse a GameSummary from an APIResponse

        :param response: The APIResponse object containing the GameSummary data.
        :type response: APIResponse
        :return: A GameSummary object constructed from the data given in the APIResponse
        :rtype: GameSummary
        """
        ret_val : DatasetManifest

        if response.Value is not None:
            ret_val = DatasetManifest.FromDict(raw_dict=response.Value)
        else:
            raise ValueError(f"Response for DataSummary contained no values!")

        return ret_val