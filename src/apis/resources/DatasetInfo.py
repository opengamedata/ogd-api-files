# import standard libraries
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
from apis.configs.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams
from utils.utils import GetFileList, MatchDatasetRequest

class DatasetInfo(Resource):
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
                    ret_val.RequestErrored(msg=f"GameID '{sanitary_params.GameID}' has no available datasets", status=ResponseStatus.ERR_NOTFOUND)
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
                    
                    # Date information
                    file_info["first_year"]  = _matched_dataset.Key.DateFrom.year
                    file_info["first_month"] = _matched_dataset.Key.DateFrom.month
                    file_info["last_year"]   = _matched_dataset.Key.DateTo.year
                    file_info["last_month"]  = _matched_dataset.Key.DateTo.month
                    _branch_name     = sanitary_params.GameID.lower().replace('_', '-')
                    _revision        = _matched_dataset.OGDRevision or None

                    # Files
                    file_info["raw_file"]        = f"{file_list.RemoteURL}{_matched_dataset.GameEventsFile}" if _matched_dataset.GameEventsFile is not None else None
                    file_info["events_file"]     = f"{file_list.RemoteURL}{_matched_dataset.AllEventsFile}"  if _matched_dataset.AllEventsFile  is not None else None
                    file_info["sessions_file"]   = f"{file_list.RemoteURL}{_matched_dataset.SessionsFile}"   if _matched_dataset.SessionsFile   is not None else None
                    file_info["players_file"]    = f"{file_list.RemoteURL}{_matched_dataset.PlayersFile}"    if _matched_dataset.PlayersFile    is not None else None
                    file_info["population_file"] = f"{file_list.RemoteURL}{_matched_dataset.PopulationFile}" if _matched_dataset.PopulationFile is not None else None

                    # Templates
                    file_info["events_template"]     = f"{file_list.TemplatesBase}{_matched_dataset.EventsTemplate}"     if _matched_dataset.EventsTemplate     is not None else None
                    file_info["sessions_template"]   = f"{file_list.TemplatesBase}{_matched_dataset.SessionsTemplate}"   if _matched_dataset.SessionsTemplate   is not None else None
                    file_info["players_template"]    = f"{file_list.TemplatesBase}{_matched_dataset.PlayersTemplate}"    if _matched_dataset.PlayersTemplate    is not None else None
                    file_info["population_template"] = f"{file_list.TemplatesBase}{_matched_dataset.PopulationTemplate}" if _matched_dataset.PopulationTemplate is not None else None

                    file_info["events_codespace"]   = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json"
                    file_info["sessions_codespace"] = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fplayer-template%2Fdevcontainer.json"
                    file_info["players_codespace"]  = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fsession-template%2Fdevcontainer.json"

                    # Convention for branch naming is lower-case with dashes,
                    # while game IDs are usually upper-case with underscores, so make sure we do the conversion
                    file_info["detectors_link"] = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{sanitary_params.GameID.upper()}/detectors" if _revision else None
                    file_info["features_link"]  = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{sanitary_params.GameID.upper()}/features"  if _revision else None
                    file_info["found_matching_range"] = True

                    ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=file_info)
                else:
                    _msg = f"Dataset key {_matched_dataset.Key} was invalid." if _matched_dataset else "No datasets found!"
                    ret_val.RequestErrored(msg=_msg)
            else:
                ret_val.RequestErrored(msg=f"Could not find a dataset for {sanitary_params.GameID} in {sanitary_params.Month:>02}/{sanitary_params.Year:>04}", status=ResponseStatus.ERR_NOTFOUND)

        return ret_val.AsFlaskResponse
