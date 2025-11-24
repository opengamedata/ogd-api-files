# import standard libraries
import json
from datetime import date, timedelta
from typing import Any, Dict, Optional
from urllib import request as url_request

# import 3rd-party libraries
from flask import Flask, current_app
from flask_restful import Resource, Api

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus

# import ogd libraries
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams

class FileAPI:
    """Class to define an API matching the original website API.

    This will eventually be superseded by a new version of the API,
    implementing the same functionality, but with cleaner endpoint routes/naming.
    """

    server_config : FileAPIConfig

    # TODO: Remove this action and dependencies (interfaces, config) if we're certain they won't be needed.
    # The SQL for BigQuery did take a bit of effort to compose, but could always be retrieved from old commits

    @staticmethod
    def register(app:Flask, settings:FileAPIConfig):
        """Set up the Legacy Web api in a flask app.

        :param app: _description_
        :type app: Flask
        """
        # Expected WSGIScriptAlias URL path is /data
        api = Api(app)
        api.add_resource(FileAPI.GameList, '/games/list')
        api.add_resource(FileAPI.GameDatasets, '/games/<game_id>/datasets/list')
        api.add_resource(FileAPI.GameDatasetInfo,  '/games/<game_id>/datasets/<month>/<year>/files/')
        FileAPI.server_config = settings

    class GameList(Resource):
        """
        Get the per-month number of sessions for a given game

        Inputs:
        - Game ID
        Uses:
        - Index file list
        Outputs:
        - Session count for each month of game's data
        """
        def get(self):
            ret_val = APIResponse.Default(req_type=RESTType.GET)

            # Pull the file list data into a dictionary
            file_list_response                             = url_request.urlopen(FileAPI.server_config.FileListURL)
            file_list_json     : Dict[str, Dict[str, Any]] = json.loads(file_list_response.read())
            file_list          : DatasetRepositoryConfig   = DatasetRepositoryConfig.FromDict(name="file_list", unparsed_elements=file_list_json)

            # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
            if file_list.Games is None or len(file_list.Games) < 1:
                ret_val.ServerErrored(msg=f"Game list not found, or had no datasets listed")
                return ret_val.AsFlaskResponse

            game_ids = [game for game in file_list.Games.keys()]

            responseData = { "game_ids": game_ids }
            ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=responseData)

            return ret_val.AsFlaskResponse

    class GameDatasets(Resource):
        """
        Get the per-month number of sessions for a given game

        Inputs:
        - Game ID
        Uses:
        - Index file list
        Outputs:
        - Session count for each month of game's data
        """
        def get(self, game_id):
            ret_val = APIResponse.Default(req_type=RESTType.GET)
            
            game_id = SanitizedParams.sanitizeGameId(game_id)
            if game_id is None or game_id == "":
                ret_val.RequestErrored(msg=f"Bad GameID '{game_id}'")
                return ret_val.AsFlaskResponse

            # Pull the file list data into a dictionary
            file_list_response                             = url_request.urlopen(FileAPI.server_config.FileListURL)
            file_list_json     : Dict[str, Dict[str, Any]] = json.loads(file_list_response.read())
            # HACK to make sure we've got a remote_url, working around bug in RepositoryIndexingConfig FromDict(...) implementation.
            if "CONFIG" in file_list_json.keys() and isinstance(file_list_json["CONFIG"], dict):
                if not "remote_url" in file_list_json["CONFIG"].keys():
                    file_list_json["CONFIG"]["remote_url"] = file_list_json["CONFIG"].get("files_base", "https://opengamedata.fielddaylab.wisc.edu/")
                if not "templates_url" in file_list_json["CONFIG"].keys():
                    file_list_json["CONFIG"]["templates_url"] = file_list_json["CONFIG"].get("templates_base", "https://github.com/opengamedata/opengamedata-templates")
            file_list          : DatasetRepositoryConfig   = DatasetRepositoryConfig.FromDict(name="file_list", unparsed_elements=file_list_json)
            game_datasets      : DatasetCollectionSchema   = file_list.Games.get(game_id, DatasetCollectionSchema.Default())

            # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
            if not game_id in file_list.Games or len(file_list.Games[game_id].Datasets) == 0:
                ret_val.ServerErrored(msg=f"GameID '{game_id}' not found in list of games with datasets, or had no datasets listed")
                return ret_val.AsFlaskResponse

            first_month = None
            first_year  = None
            lastYear    = None
            lastMonth   = None

            total_sessions_by_yyyymm = {}

            # rangeKey format is GAMEID_YYYYMMDD_to_YYYYMMDD or GAME_ID_YYYYMMDD_to_YYYYYMMDD
            for _datset_id,_dataset in game_datasets.Datasets.items():

                # If this rangeKey matches the expected format
                if _dataset.Key.DateFrom: # len(rangeKeyParts) == 4:
                    # Capture the number of sessions for this YYYYMM
                    _year_month = _dataset.Key.DateFrom.strftime("%Y%m")
                    total_sessions_by_yyyymm[_year_month] = _dataset.SessionCount

                    # The ranges in file_list_json should be chronologically ordered, but manually determining the first & last months here just in case
                    if first_year is None or first_month is None or _dataset.Key.DateFrom.year < first_year:
                        first_year = _dataset.Key.DateFrom.year
                        first_month = _dataset.Key.DateFrom.month
                    elif _dataset.Key.DateFrom.year == first_year and _dataset.Key.DateFrom.month < first_month:
                        first_month = _dataset.Key.DateFrom.month
                    
                    if lastYear is None or lastMonth is None or _dataset.Key.DateFrom.year > lastYear:
                        lastYear = _dataset.Key.DateFrom.year
                        lastMonth = _dataset.Key.DateFrom.month
                    elif lastYear == _dataset.Key.DateFrom.year and lastMonth < _dataset.Key.DateFrom.month:
                        lastMonth = _dataset.Key.DateFrom.month


            # Iterate through all of the months from the first month+year to last month+year, since the ranges have gaps
            # Default the number of sessions to zero for months we don't have data
            sessions = []
            if first_year is not None and first_month is not None and lastYear is not None and lastMonth is not None:
                startRangeMonth = first_month
                for year in range(first_year, lastYear + 1):
                    endRangeMonth = lastMonth if year == lastYear else 12
                    for month in range(startRangeMonth, endRangeMonth + 1):
                        # If file_list.json has an entry for this month
                        _year_month = f"{year}{month:02}" # {month:02} => 0-pad width 2
                        sessions.append({ "year": year, "month": month, "total_sessions": total_sessions_by_yyyymm.get(_year_month, 0)})
                    startRangeMonth = 1

            responseData = { "game_id": game_id, "datasets": sessions }
            ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=responseData)

            return ret_val.AsFlaskResponse

    class GameDatasetInfo(Resource):
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

            last_month = date.today().replace(day=1) - timedelta(days=1)
            sanitized_request = SanitizedParams(game_id=game_id, year=year, month=month, default_date=last_month)

        # 1. Get the list of datasets available on the server, for given game.
            file_list_response                             = url_request.urlopen(FileAPI.server_config.FileListURL)
            file_list_json     : Dict[str, Dict[str, Any]] = json.loads(file_list_response.read())
            # HACK to make sure we've got a remote_url, working around bug in RepositoryIndexingConfig FromDict(...) implementation.
            if "CONFIG" in file_list_json.keys() and isinstance(file_list_json["CONFIG"], dict):
                if not "remote_url" in file_list_json["CONFIG"].keys():
                    file_list_json["CONFIG"]["remote_url"] = file_list_json["CONFIG"].get("files_base", "https://opengamedata.fielddaylab.wisc.edu/")
                if not "templates_url" in file_list_json["CONFIG"].keys():
                    file_list_json["CONFIG"]["templates_url"] = file_list_json["CONFIG"].get("templates_base", "https://github.com/opengamedata/opengamedata-templates")
            file_list          : DatasetRepositoryConfig   = DatasetRepositoryConfig.FromDict(name="file_list", unparsed_elements=file_list_json)
            game_datasets      : DatasetCollectionSchema   = file_list.Games.get(sanitized_request.GameID or "NO GAME REQUESTED", DatasetCollectionSchema.Default())

            # If we couldn't find the requested game in file_list.json, or the game didn't have any date ranges, skip.
            if (sanitized_request.GameID is None):
                ret_val.RequestErrored(msg=f"Bad GameID '{sanitized_request.GameID}'")
                return ret_val.AsFlaskResponse
            elif (len(game_datasets.Datasets) == 0):
                ret_val.ServerErrored(msg=f"GameID '{sanitized_request.GameID}' did not have available datasets")
                return ret_val.AsFlaskResponse
            # Else, continue on.

        # 2. Search for the most recently modified dataset that contains the requested month and year
            _matched_dataset : Optional[DatasetSchema] = None
            # Find the best match of a dataset to the requested month-year.
            # If there was no requested month-year, we skip this step.
            for _key, _dataset_schema in game_datasets.Datasets.items():
                if _dataset_schema.Key.DateFrom and _dataset_schema.Key.DateTo:
                    # If this range contains the given year & month
                    if (sanitized_request.Year >= _dataset_schema.Key.DateFrom.year \
                    and sanitized_request.Month >= _dataset_schema.Key.DateFrom.month \
                    and sanitized_request.Year <= _dataset_schema.Key.DateTo.year \
                    and sanitized_request.Month <= _dataset_schema.Key.DateTo.month):
                        if _dataset_schema.IsNewerThan(_matched_dataset):
                            _matched_dataset = _dataset_schema
                else:
                    current_app.logger.debug(f"Dataset key {_dataset_schema.Key} was invalid.")

            if _matched_dataset is None:
                _matched_dataset = list(game_datasets.Datasets.values())[-1]
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
                _branch_name     = sanitized_request.GameID.lower().replace('_', '-')
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
                file_info["detectors_link"] = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{_branch_name.upper()}/detectors" if _revision else None
                file_info["features_link"]  = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{_branch_name.upper()}/features"  if _revision else None
                file_info["found_matching_range"] = True

                ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=file_info)
            else:
                ret_val.RequestErrored(msg=f"Dataset key {_matched_dataset.Key} was invalid.")

            return ret_val.AsFlaskResponse