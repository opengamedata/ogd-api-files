# import standard libraries
import json
from datetime import date, timedelta
from logging.config import dictConfig
from typing import Any, Dict, Optional
from urllib import request as url_request

# import 3rd-party libraries
from flask import Flask, request, Response, current_app
from flask_restful import Resource, Api, reqparse
from flask_restful.inputs import datetime_from_iso8601
from werkzeug.exceptions import BadRequest

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType

# import ogd libraries
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.schemas.datasets.FileListSchema import FileListSchema, GameDatasetCollectionSchema

# import local files
from schemas.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams
from interfaces.BigQueryInterface import BigQueryInterface

class LegacyWebAPI:
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
        api.add_resource(LegacyWebAPI.Hello,               '/')
        # api.add_resource(LegacyWebAPI.Version,             '/version')
        api.add_resource(LegacyWebAPI.GameUsageByMonth,    '/getGameUsageByMonth')
        api.add_resource(LegacyWebAPI.MonthlyGameUsage,    '/getMonthlyGameUsage')
        api.add_resource(LegacyWebAPI.GameFileInfoByMonth, '/getGameFileInfoByMonth')
        LegacyWebAPI.server_config = settings

    # Basic response if someone just hits the home path to say "hello"
    class Hello(Resource):
        """
        Basic response if someone just hits the home path to say "hello"
        """
        def get(self) -> Response:
            ret_val = APIResponse.Default(req_type=RESTType.GET)

            _msg = "hello, world"
            ret_val.RequestSucceeded(msg=_msg, val={})

            return ret_val.AsFlaskResponse

    # Get the version of the API.
    # class Version(Resource):
    #     """
    #     Get the version of the API.
    #     """
    #     def get(self) -> Response:
    #         ret_val = APIResponse.Default(req_type=RESTType.GET)

    #         _ver = LegacyWebAPI.server_config.Version
    #         ret_val.RequestSucceeded(msg=f"Retrieved version", val={"version":_ver})

    #         return ret_val.AsFlaskResponse

    # Get game usage statistics for a given game, year, and month
    class GameUsageByMonth(Resource):
        """
        Get game usage statistics for a given game, year, and month

        NOTE : Does not appear to be in use - this looks to be a placeholder for retrieving live monthly usage stats from BigQuery.
        
        Inputs:
        - Game ID
        - Month
        - Year
        Outputs:
        - Month's session count
        - Daily session counts for month
        """
        def get(self) -> Response:
            ret_val = APIResponse.Default(req_type=RESTType.GET)

            last_month = date.today().replace(day=1) - timedelta(days=1)
            sanitized_request = SanitizedParams.FromRequest(default_date=last_month)

            if sanitized_request.GameID is None or sanitized_request.GameID == "":
                ret_val.RequestErrored(msg=f"Bad GameID '{sanitized_request.GameID}'")
                return ret_val.AsFlaskResponse

            # If we don't have a mapping for the given game
            if not sanitized_request.GameID in LegacyWebAPI.server_config.GameMapping:
                ret_val.ServerErrored(msg=f"GameID '{sanitized_request.GameID}' not found in available games")
                return ret_val.AsFlaskResponse

            total_monthly_sessions = 0
            sessions_by_day = {}

            bqInterface = BigQueryInterface(LegacyWebAPI.server_config.GameMapping[sanitized_request.GameID])
            total_monthly_sessions = bqInterface.GetTotalSessionsForMonth(sanitized_request.Year, sanitized_request.Month)
            sessions_by_day        = bqInterface.GetSessionsPerDayForMonth(sanitized_request.Year, sanitized_request.Month)

            responseData = {
                "game_id": sanitized_request.GameID,
                "selected_month": sanitized_request.Month,
                "selected_year": sanitized_request.Year,
                "total_monthly_sessions": total_monthly_sessions,
                "sessions_by_day": sessions_by_day
            }
            ret_val.RequestSucceeded(msg="Retrieved game usage by month", val=responseData)

            return ret_val.AsFlaskResponse

    class MonthlyGameUsage(Resource):
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
            
            # Extract a sanitized game_id from the query string
            parser = reqparse.RequestParser()
            parser.add_argument("game_id", type=str, nullable=True, required=False, default="",                 location="args")
            args : Dict[str, Any] = parser.parse_args()
            game_id = SanitizedParams.sanitizeGameId(args.get("game_id") or "")
            
            if game_id is None or game_id == "":
                ret_val.RequestErrored(msg=f"Bad GameID '{game_id}'")
                return ret_val.AsFlaskResponse

            # Pull the file list data into a dictionary
            file_list_response                             = url_request.urlopen(LegacyWebAPI.server_config.FileListURL)
            file_list_json     : Dict[str, Dict[str, Any]] = json.loads(file_list_response.read())
            file_list          : FileListSchema              = FileListSchema(name="file_list", all_elements=file_list_json)
            game_datasets      : GameDatasetCollectionSchema = file_list.Games.get(game_id or "NO GAME REQUESTED", GameDatasetCollectionSchema.EmptySchema())

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
            for _key,_dataset in game_datasets.Datasets.items():

                # If this rangeKey matches the expected format
                if _dataset.Key.IsValid: # len(rangeKeyParts) == 4:
                    # Capture the number of sessions for this YYYYMM
                    _year_month = str(_dataset.Key.FromYear) + str(_dataset.Key.FromMonth).zfill(2)
                    total_sessions_by_yyyymm[_year_month] = _dataset.SessionCount

                    # The ranges in file_list_json should be chronologically ordered, but manually determining the first & last months here just in case
                    if first_year is None or first_month is None or _dataset.Key.FromYear < first_year:
                        first_year = _dataset.Key.FromYear
                        first_month = _dataset.Key.FromMonth
                    elif _dataset.Key.FromYear == first_year and _dataset.Key.FromMonth < first_month:
                        first_month = _dataset.Key.FromMonth
                    
                    if lastYear is None or lastMonth is None or _dataset.Key.FromYear > lastYear:
                        lastYear = _dataset.Key.FromYear
                        lastMonth = _dataset.Key.FromMonth
                    elif lastYear == _dataset.Key.FromYear and lastMonth < _dataset.Key.FromMonth:
                        lastMonth = _dataset.Key.FromMonth


            # Iterate through all of the months from the first month+year to last month+year, since the ranges have gaps
            # Default the number of sessions to zero for months we don't have data
            sessions = []
            if first_year is not None and first_month is not None and lastYear is not None and lastMonth is not None:
                startRangeMonth = first_month
                for year in range(first_year, lastYear + 1):
                    endRangeMonth = lastMonth if year == lastYear else 12
                    for month in range(startRangeMonth, endRangeMonth + 1):
                        # If file_list.json has an entry for this month
                        _year_month = str(year) + str(month).zfill(2)
                        sessions.append({ "year": year, "month": month, "total_sessions": total_sessions_by_yyyymm.get(_year_month, 0)})
                    startRangeMonth = 1

            responseData = { "game_id": game_id, "sessions": sessions }
            ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=responseData)

            return ret_val.AsFlaskResponse

    class GameFileInfoByMonth(Resource):
        """
        Get info on the files that are available for the given game in the given month & year

        Inputs:
        - Game ID
        - Year
        - Month
        Outputs:
        - DatasetSchema of most recently-exported dataset for game in month
        """
        def get(self):
            ret_val = APIResponse.Default(req_type=RESTType.GET)

            last_month = date.today().replace(day=1) - timedelta(days=1)
            sanitized_request = SanitizedParams.FromRequest(default_date=last_month)

        # 1. Get the list of datasets available on the server, for given game.
            file_list_response                               = url_request.urlopen(LegacyWebAPI.server_config.FileListURL)
            file_list_json     : Dict[str, Dict[str, Any]]   = json.loads(file_list_response.read())
            file_list          : FileListSchema              = FileListSchema(name="file_list", all_elements=file_list_json)
            game_datasets      : GameDatasetCollectionSchema = file_list.Games.get(sanitized_request.GameID or "NO GAME REQUESTED", GameDatasetCollectionSchema.EmptySchema())

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
                if _dataset_schema.Key.IsValid:
                    # If this range contains the given year & month
                    if (sanitized_request.Year >= _dataset_schema.Key.FromYear \
                    and sanitized_request.Month >= _dataset_schema.Key.FromMonth \
                    and sanitized_request.Year <= _dataset_schema.Key.ToYear \
                    and sanitized_request.Month <= _dataset_schema.Key.ToMonth):
                        if _dataset_schema.IsNewerThan(_matched_dataset):
                            _matched_dataset = _dataset_schema
                else:
                    current_app.logger.debug(f"Dataset key {_dataset_schema.Key} was invalid.")

            if _matched_dataset is None:
                _matched_dataset = list(game_datasets.Datasets.values())[-1]
            file_info = {}

            # If this range contains the given year & month
            # Base URLs
            CODESPACES_BASE_URL : str = "https://codespaces.new/opengamedata/opengamedata-samples/tree/"
            GITHUB_BASE_URL     : str = "https://github.com/opengamedata/opengamedata-core/tree/"
            
            # Date information
            file_info["first_year"]  = _matched_dataset.Key.FromYear
            file_info["first_month"] = _matched_dataset.Key.FromMonth
            file_info["last_year"]   = _matched_dataset.Key.ToYear
            file_info["last_month"]  = _matched_dataset.Key.ToMonth
            _branch_name     = sanitized_request.GameID.lower().replace('_', '-')
            _revision        = _matched_dataset.OGDRevision or None

            # Files
            file_info["raw_file"]        = f"{file_list.Config.FilesBase}{_matched_dataset.RawFile}"        if _matched_dataset.RawFile        is not None else None
            file_info["events_file"]     = f"{file_list.Config.FilesBase}{_matched_dataset.EventsFile}"     if _matched_dataset.EventsFile     is not None else None
            file_info["sessions_file"]   = f"{file_list.Config.FilesBase}{_matched_dataset.SessionsFile}"   if _matched_dataset.SessionsFile   is not None else None
            file_info["players_file"]    = f"{file_list.Config.FilesBase}{_matched_dataset.PlayersFile}"    if _matched_dataset.PlayersFile    is not None else None
            file_info["population_file"] = f"{file_list.Config.FilesBase}{_matched_dataset.PopulationFile}" if _matched_dataset.PopulationFile is not None else None

            # Templates
            file_info["events_template"]     = f"{file_list.Config.TemplatesBase}{_matched_dataset.EventsTemplate}"     if _matched_dataset.EventsTemplate     is not None else None
            file_info["sessions_template"]   = f"{file_list.Config.TemplatesBase}{_matched_dataset.SessionsTemplate}"   if _matched_dataset.SessionsTemplate   is not None else None
            file_info["players_template"]    = f"{file_list.Config.TemplatesBase}{_matched_dataset.PlayersTemplate}"    if _matched_dataset.PlayersTemplate    is not None else None
            file_info["population_template"] = f"{file_list.Config.TemplatesBase}{_matched_dataset.PopulationTemplate}" if _matched_dataset.PopulationTemplate is not None else None

            file_info["events_codespace"]   = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json"
            file_info["sessions_codespace"] = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fplayer-template%2Fdevcontainer.json"
            file_info["players_codespace"]  = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fsession-template%2Fdevcontainer.json"

            # Convention for branch naming is lower-case with dashes,
            # while game IDs are usually upper-case with underscores, so make sure we do the conversion
            file_info["detectors_link"] = f"{GITHUB_BASE_URL}{_revision}/games/{_branch_name}/detectors" if _revision else None
            file_info["features_link"]  = f"{GITHUB_BASE_URL}{_revision}/games/{_branch_name}/features"  if _revision else None
            file_info["found_matching_range"] = True

            ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=file_info)

            return ret_val.AsFlaskResponse