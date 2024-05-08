# import standard libraries
import json
from calendar import monthrange
from datetime import date, timedelta
from logging.config import dictConfig
from typing import Any, Dict, Optional
from urllib import request as url_request

# import 3rd-party libraries
from flask import Flask, send_file, request
from flask_cors import CORS

# import our app libraries
from models.APIResponse import APIResponse
from schemas.DatasetSchema import DatasetSchema
from schemas.FileListSchema import FileListSchema, GameDatasetCollectionSchema
from models.SanitizedParams import SanitizedParams
from interfaces.BigQueryInterface import BigQueryInterface

# By default we'll log to the WSGI errors stream which ends up in the Apache error log
logHandlers = {
        'wsgi': { 
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream', 
            'formatter': 'default'
            }
    }

logRootHandlers = ['wsgi']

# NOTE: Commenting out the dedicated log file for this app. The code functions fine, but 
# getting the permissions set correctly isn't a priority right now

# If a dedicated log file is defined for this Flask app, we'll also log there
# Ensure this is in a directory writable by the user executing the WSGI app (likely the web daemon - www-data or apache)
# if "OGD_FLASK_APP_LOG_FILE" in os.environ:
#     logHandlers['wsgi_app_file'] = {
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.environ["OGD_FLASK_APP_LOG_FILE"],
#             'maxBytes': 100000000, # 100 MB
#             'backupCount': 10, # Up to 10 rotated files
#             'formatter': 'default'
#     }

#     logRootHandlers.append('wsgi_app_file')

# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': logHandlers,
#     'root': {
#         'level': 'INFO',
#         'handlers': logRootHandlers
#     }
# })

application = Flask(__name__)

# Allow cross-origin requests from any origin by default
# This presents minimal risk to visitors since the API merely retrieves non-sensitive data
# NOTE: Comment this out if the web server itself is configured to send an Access-Control-Allow-Origin header, so we don't have a duplicate header
CORS(application)

# Now that logging is set up, import our local config settings
from config.config import settings
application.logger.setLevel(settings['DEBUG_LEVEL'])


# TODO: Remove this action and dependencies (interfaces, config) if we're certain they won't be needed.
# The SQL for BigQuery did take a bit of effort to compose, but could always be retrieved from old commits

@application.route('/', methods=['GET'])
def Hello():
    """
    Basic response if someone just hits the home path to say "hello"
    """

    responseObj = {
        "message": "hello, world"
    }

    return APIResponse(success=True, data=responseObj).ToDict()

@application.route('/version', methods=['GET'])
def get_api_version():

    responseObj = {
        "message": settings["API_VERSION"]
    }

    return APIResponse(True, responseObj).ToDict()

# Get game usage statistics for a given game, year, and month
@application.route('/getGameUsageByMonth', methods=['GET'])
def getGameUsageByMonth():
    """
    Get game usage statistics for a given game, year, and month
    
    Inputs:
    - Game ID
    - Month
    - Year
    Outputs:
    - Month's session count
    - Daily session counts for month
    """

    last_month = date.today().replace(day=1) - timedelta(days=1)
    sanitized_request = SanitizedParams.FromRequest(default_date=last_month)

    if sanitized_request.GameID is None or sanitized_request.GameID == "":
        return APIResponse(False, None).ToDict()

    # If we don't have a mapping for the given game
    if not sanitized_request.GameID in settings["BIGQUERY_GAME_MAPPING"]:
        return APIResponse(False, None).ToDict()

    total_monthly_sessions = 0
    sessions_by_day = {}

    bqInterface = BigQueryInterface(settings["BIGQUERY_GAME_MAPPING"][sanitized_request.GameID])
    total_monthly_sessions = bqInterface.GetTotalSessionsForMonth(sanitized_request.Year, sanitized_request.Month)
    sessions_by_day        = bqInterface.GetSessionsPerDayForMonth(sanitized_request.Year, sanitized_request.Month)

    responseObj = {
        "game_id": sanitized_request.GameID,
        "selected_month": sanitized_request.Month,
        "selected_year": sanitized_request.Year,
        "total_monthly_sessions": total_monthly_sessions,
        "sessions_by_day": sessions_by_day
    }

    return APIResponse(True, responseObj).ToDict()

@application.route("/getMonthlyGameUsage", methods=['GET'])
def getMonthlyGameUsage():
    """
    Get the per-month number of sessions for a given game

    Inputs:
    - Game ID
    Uses:
    - Index file list
    Outputs:
    - Session count for each month of game's data
    """
    
    # Extract a sanitized game_id from the query string
    game_id = SanitizedParams.sanitizeGameId(request.args.get("game_id", default = "", type=str))
     
    if game_id is None or game_id == "":
        return APIResponse(False, None).ToDict()

    # Pull the file list data into a dictionary
    file_list_url      : str                       = settings.get("FILE_LIST_URL", "https://opengamedata.fielddaylab.wisc.edu/data/file_list.json")
    file_list_response                             = url_request.urlopen(file_list_url)
    file_list_json     : Dict[str, Dict[str, Any]] = json.loads(file_list_response.read())
    file_list          : FileListSchema              = FileListSchema(name="file_list", all_elements=file_list_json)
    game_datasets      : GameDatasetCollectionSchema = file_list.Games.get(game_id or "NO GAME REQUESTED", GameDatasetCollectionSchema.EmptySchema())

    # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
    if not game_id in file_list.Games or len(file_list.Games[game_id].Datasets) == 0:
        return APIResponse(False, None).ToDict()

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
    return APIResponse(True, responseData).ToDict()

@application.route('/getGameFileInfoByMonth', methods=['GET'])
def getGameFileInfoByMonth():
    """
    Get info on the files that are available for the given game in the given month & year

    Inputs:
    - Game ID
    - Year
    - Month
    Outputs:
    - DatasetSchema of most recently-exported dataset for game in month
    """
    last_month = date.today().replace(day=1) - timedelta(days=1)
    sanitized_request = SanitizedParams.FromRequest(default_date=last_month)

# 1. Get the list of datasets available on the server, for given game.
    file_list_url      : str                         = settings.get("FILE_LIST_URL", "https://opengamedata.fielddaylab.wisc.edu/data/file_list.json")
    file_list_response                               = url_request.urlopen(file_list_url)
    file_list_json     : Dict[str, Dict[str, Any]]   = json.loads(file_list_response.read())
    file_list          : FileListSchema              = FileListSchema(name="file_list", all_elements=file_list_json)
    game_datasets      : GameDatasetCollectionSchema = file_list.Games.get(sanitized_request.GameID or "NO GAME REQUESTED", GameDatasetCollectionSchema.EmptySchema())

    # If we couldn't find the requested game in file_list.json, or the game didn't have any date ranges, skip.
    if (sanitized_request.GameID is None) or (len(game_datasets.Datasets) == 0):
        return APIResponse(success=False, data=None).ToDict()
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
            application.logger.debug(f"Dataset key {_dataset_schema.Key} was invalid.")

    if _matched_dataset is not None:
        file_info = {}

        # If this range contains the given year & month
        # Base URLs
        CODESPACES_BASE_URL : str           = "https://codespaces.new/opengamedata/opengamedata-samples/tree/"
        GITHUB_BASE_URL     : str           = "https://github.com/opengamedata/opengamedata-core/tree/"
        
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
    else:
        return APIResponse(success=False, data=None).ToDict()

    return APIResponse(True, file_info).ToDict()

