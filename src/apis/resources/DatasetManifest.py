# import standard libraries
import json
from urllib import request as urlrequest
from typing import Optional

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams
from utils.utils import GetFileList, MatchDatasetRequest

class DatasetManifest(Resource):
    """
    Get info on the files that are available for the given game in the given month & year

    Inputs:
    - Game ID
    - Year
    - Month
    Outputs:
    - DatasetSchema of most recently-exported dataset for game in month
    """
    def get(self, game_id, month, year):
        ret_val = APIResponse.Default(req_type=RESTType.GET)

        try:
            sanitary_params = SanitizedParams.FromParams(game_id=game_id, year=year, month=month)

        # 1. Get the list of datasets available on the server, for given game.
            if sanitary_params:
                cfg           : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
                file_list     : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
                game_datasets : DatasetCollectionSchema = file_list.Games.get(sanitary_params.GameID or "NO GAME REQUESTED", DatasetCollectionSchema.Default())

                # If we couldn't find the requested game in file_list.json, or the game didn't have any date ranges, skip.
                if (sanitary_params.GameID is None):
                    ret_val.RequestErrored(msg=f"Bad GameID '{sanitary_params.GameID}'")
                    return ret_val.AsFlaskResponse
                elif (len(game_datasets.Datasets) == 0):
                    ret_val.RequestErrored(msg=f"GameID '{sanitary_params.GameID}' has no available datasets", status=ResponseStatus.NOT_FOUND)
                    return ret_val.AsFlaskResponse
            else:
                raise ValueError("Could not process inputs!")
        except Exception as err:
            current_app.logger.error(f"{type(err)} error processing request inputs:\n{err}")
            ret_val.ServerErrored("Unexpected error processing request inputs.")
        else:
        # 2. Search for the most recently modified dataset that contains the requested month and year
            _matched_dataset : Optional[DatasetSchema] = MatchDatasetRequest(sanitary_request=sanitary_params, available_datasets=game_datasets)

            if _matched_dataset:
                if _matched_dataset.Key.DateFrom and _matched_dataset.Key.DateTo:
                    file_info = {}

                    # If this range contains the given year & month
                    # Base URLs
                    CODESPACES_BASE_URL : str = "https://codespaces.new/opengamedata/opengamedata-samples/tree/"
                    GITHUB_BASE_URL     : str = "https://github.com/opengamedata/opengamedata-core/tree/"
                    
                    # Game information
                    file_info["game_id"]     = sanitary_params.GameID

                    # Population information
                    file_info["population"] = {}
                    file_info["population"]["first_year"]  = _matched_dataset.Key.DateFrom.year
                    file_info["population"]["first_month"] = _matched_dataset.Key.DateFrom.month
                    file_info["population"]["last_year"]   = _matched_dataset.Key.DateTo.year
                    file_info["population"]["last_month"]  = _matched_dataset.Key.DateTo.month
                    _branch_name     = sanitary_params.GameID.lower().replace('_', '-')
                    _revision        = _matched_dataset.OGDRevision or None

                    # File outputs
                    file_info["output"] = {}
                    file_info["output"]["raw_file"]        = f"{file_list.RemoteURL}{_matched_dataset.GameEventsFile}" if _matched_dataset.GameEventsFile is not None else None
                    file_info["output"]["events_file"]     = f"{file_list.RemoteURL}{_matched_dataset.AllEventsFile}"  if _matched_dataset.AllEventsFile  is not None else None
                    file_info["output"]["sessions_file"]   = f"{file_list.RemoteURL}{_matched_dataset.SessionsFile}"   if _matched_dataset.SessionsFile   is not None else None
                    file_info["output"]["players_file"]    = f"{file_list.RemoteURL}{_matched_dataset.PlayersFile}"    if _matched_dataset.PlayersFile    is not None else None
                    file_info["output"]["population_file"] = f"{file_list.RemoteURL}{_matched_dataset.PopulationFile}" if _matched_dataset.PopulationFile is not None else None

                    # Versioning/traceability
                    file_info["versioning"] = {}
                    # Convention for branch naming is lower-case with dashes,
                    # while game IDs are usually upper-case with underscores, so make sure we do the conversion
                    file_info["versioning"]["detectors_link"] = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{sanitary_params.GameID.upper()}/detectors" if _revision else None
                    file_info["versioning"]["features_link"]  = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{sanitary_params.GameID.upper()}/features"  if _revision else None

                    raw_url = f"https://raw.githubusercontent.com/opengamedata/ogd-core/refs/heads/main/src/ogd/games/{sanitary_params.GameID.upper()}/schemas/{sanitary_params.GameID.upper()}.json.template"
                    with urlrequest.urlopen(raw_url) as _conn:
                        try:
                            raw_schema = _conn.read().decode('utf-8')
                        except Exception:
                            file_info["game_state"] = "Could not retrieve schema"
                            file_info["events"] = "Could not retrieve schema"
                            file_info["features"] = "Could not retrieve schema"
                        else:
                            schema = json.loads(raw_schema)
                            file_info["game_state"] = schema.get("game_state", "Could not find game state in schema")
                            file_info["events"] = schema.get("events", "Could not find event listings in schema")
                            file_info["features"] = schema.get("features", "Could not find feature configs in schema")

                    ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=file_info)
                else:
                    _msg = f"Dataset key {_matched_dataset.Key} was invalid." if _matched_dataset else "No datasets found!"
                    ret_val.RequestErrored(msg=_msg)
            else:
                ret_val.RequestErrored(msg=f"Could not find a dataset for {sanitary_params.GameID} in {sanitary_params.Month:>02}/{sanitary_params.Year:>04}", status=ResponseStatus.NOT_FOUND)

        return ret_val.AsFlaskResponse
