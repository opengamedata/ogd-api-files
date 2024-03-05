# import standard libraries
import sys, os, re, datetime, json
from calendar import monthrange
from logging.config import dictConfig
from typing import Optional
from urllib import request as url_request

# import 3rd-party libraries
from flask import Flask, send_file, request
from flask_cors import CORS

# import our app libraries
from models.APIResponse import APIResponse
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

class DatasetKey:
    """Simple little class to make logic with dataset keys easier
    """
    def __init__(self, key:str, game_id:str):
        _dataset_date_range = key[len(game_id):]
        _dataset_date_range_parts = _dataset_date_range.split("_")
        # If this _dataset_key matches the expected format,
        # i.e. spit is: ["", "YYYYMMDD", "to", "YYYYMMDD"]
        if len(_dataset_date_range_parts) == 4:
            self._fromYear  = int(_dataset_date_range_parts[1][0:4])
            self._fromMonth = int(_dataset_date_range_parts[1][4:6])
            self._toYear    = int(_dataset_date_range_parts[3][0:4])
            self._toMonth   = int(_dataset_date_range_parts[3][4:6])
        else:
            self._fromYear  = None
            self._fromMonth = None
            self._toYear    = None
            self._toMonth   = None
    
    @property
    def IsValid(self) -> bool:
        return  self._fromYear  is not None \
            and self._fromMonth is not None \
            and self._toYear    is not None \
            and self._toMonth   is not None
    @property
    def FromYear(self) -> int:
        return self._fromYear or -1
    @property
    def FromMonth(self) -> int:
        return self._fromMonth or -1
    @property
    def ToYear(self) -> int:
        return self._toYear or -1
    @property
    def ToMonth(self) -> int:
        return self._toMonth or -1


class SanitizedParams:
    """Dumb struct to store the sanitized params from a request
    """
    def __init__(self, game_id:Optional[str], year:int, month:int):
        self._game_id : Optional[str] = game_id
        self._year    : int           = year
        self._month   : int           = month
    
    @property
    def GameID(self) -> Optional[str]:
        return self._game_id
    @property
    def Year(self) -> int:
        return self._year
    @property
    def Month(self) -> int:
        return self._month

    # If the given game_id contains allowed characters, return it in UPPERCASE, otherwise return empty string
    @staticmethod
    def sanitizeGameId(game_id: str) -> str:
        if re.search("^[A-Za-z_]+$", game_id) is None:
            game_id = ""
        return game_id.upper()

    # Shared utility function to retrieve game_id, year, and month from the request's query string.
    # Defaults are used if a value was not given or is invalid
    @staticmethod
    def FromRequest() -> 'SanitizedParams':

        now_date = datetime.date.today()

        # Extract query string parameters
        game_id = SanitizedParams.sanitizeGameId(request.args.get("game_id", default ="", type=str))
        year = request.args.get("year",   default=now_date.year, type=int)
        month = request.args.get("month", default=now_date.month, type=int)

        if game_id == "":
            game_id = None
        
        if month < 1 or month > 12:
            month = now_date.month

        if year < 2000 or year > now_date.year:
            year = now_date.year

        return SanitizedParams(game_id=game_id, year=year, month=month)
        return { "game_id": game_id, "year": year, "month": month }

# TODO: Remove this action and dependencies (interfaces, config) if we're certain they won't be needed.
# The SQL for BigQuery did take a bit of effort to compose, but could always be retrieved from old commits

# Basic response if someone just hits the home path to say "hello"
@application.route('/', methods=['GET'])
def get_hello():

    responseObj = {
        "message": "hello, world"
    }

    return APIResponse(True, responseObj).ToDict()

# Get game usage statistics for a given game, year, and month
@application.route('/getGameUsageByMonth', methods=['GET'])
def get_game_usage_by_month():

    sanitizedInput = SanitizedParams.FromRequest()

    if sanitizedInput.GameID is None or sanitizedInput.GameID == "":
        return APIResponse(False, None).ToDict()

    # If we don't have a mapping for the given game
    if not sanitizedInput.GameID in settings["BIGQUERY_GAME_MAPPING"]:
        return APIResponse(False, None).ToDict()

    total_monthly_sessions = 0
    sessions_by_day = {}

    bqInterface = BigQueryInterface(settings["BIGQUERY_GAME_MAPPING"][sanitizedInput.GameID])
    total_monthly_sessions = bqInterface.GetTotalSessionsForMonth(sanitizedInput.Year, sanitizedInput.Month)
    sessions_by_day        = bqInterface.GetSessionsPerDayForMonth(sanitizedInput.Year, sanitizedInput.Month)

    responseObj = {
        "game_id": sanitizedInput.GameID,
        "selected_month": sanitizedInput.Month,
        "selected_year": sanitizedInput.Year,
        "total_monthly_sessions": total_monthly_sessions,
        "sessions_by_day": sessions_by_day
    }

    return APIResponse(True, responseObj).ToDict()

# Get the per-month number of sessions for a given game
@application.route("/getMonthlyGameUsage", methods=['GET'])
def get_monthly_game_usage():
    
    # Extract a sanitized game_id from the query string
    game_id = SanitizedParams.sanitizeGameId(request.args.get("game_id", default = "", type=str))
     
    if game_id is None or game_id == "":
        return APIResponse(False, None).ToDict()

    # Pull the file list data into a dictionary
    file_list_url = 'https://opengamedata.fielddaylab.wisc.edu/data/file_list.json'
    file_list_response = url_request.urlopen(file_list_url)
    file_list_json = json.loads(file_list_response.read())

    # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
    if not game_id in file_list_json or len(file_list_json[game_id]) == 0:
        return APIResponse(False, None).ToDict()

    firstMonth = None
    firstYear = None
    lastYear = None
    lastMonth = None

    total_sessions_by_yyyymm = {}

     # rangeKey format is GAMEID_YYYYMMDD_to_YYYYMMDD or GAME_ID_YYYYMMDD_to_YYYYYMMDD
    for rangeKey in file_list_json[game_id]:

        rangeKeyWithoutGame = rangeKey[len(game_id):]
        rangeKeyParts = rangeKeyWithoutGame.split("_")

        # If this rangeKey matches the expected format
        if len(rangeKeyParts) == 4:
            year = rangeKeyParts[1][0:4]
            month = rangeKeyParts[1][4:6]

            # Capture the number of sessions for this YYYYMM
            total_sessions_by_yyyymm[year + month] = file_list_json[game_id][rangeKey]["sessions"]

            # The ranges in file_list_json should be chronologically ordered, but manually determining the first & last months here just in case
            if firstYear is None or int(year) < firstYear:
                firstYear = int(year)
                firstMonth = int(month)
            elif int(year) == firstYear and int(month) < firstMonth:
                firstMonth = int(month)
            
            if lastYear is None or int(year) > lastYear:
                lastYear = int(year)
                lastMonth = int(month)
            elif lastYear == int(year) and lastMonth < int(month):
                lastMonth = int(month)

    sessions = []
    startRangeMonth = firstMonth

    # Iterate through all of the months from the first month+year to last month+year, since the ranges have gaps
    # Default the number of sessions to zero for months we don't have data
    for year in range(firstYear, lastYear + 1):
        endRangeMonth = lastMonth if year == lastYear else 12
        for month in range(startRangeMonth, endRangeMonth + 1):
            # If file_list.json has an entry for this month
            if str(year) + str(month).zfill(2) in total_sessions_by_yyyymm:
                sessions.append({ "year": year, "month": month, "total_sessions": total_sessions_by_yyyymm[str(year) + str(month).zfill(2)]})
            else:
                sessions.append({ "year": year, "month": month, "total_sessions": 0 })
        startRangeMonth = 1

    responseData = { "game_id": game_id, "sessions": sessions }
    return APIResponse(True, responseData).ToDict()

# Get info on the files that are available for the given game in the given month & year
@application.route('/getGameFileInfoByMonth', methods=['GET'])
def get_game_file_info_by_month():
    ret_val = APIResponse(success=False, data=None).ToDict()

    sanitizedRequestParams = SanitizedParams.FromRequest()

    file_list_response = url_request.urlopen(settings.get("FILE_LIST_URL", "https://opengamedata.fielddaylab.wisc.edu/data/file_list.json"))
    file_list_json     = json.loads(file_list_response.read())

    # If we couldn't find the requested game in file_list.json, or the game didn't have any date ranges, skip.
    _game_datasets = file_list_json.get(sanitizedRequestParams.GameID, {})
    if (sanitizedRequestParams.GameID is not None) and (len(_game_datasets) > 0):
        file_info = {}
        found_matching_range = False

        # If a year and month wasn't given, we'll default to returning files & info for the last range
        if sanitizedRequestParams.Year is None or sanitizedRequestParams.Month is None:
            _last_dataset_key = list(_game_datasets)[-1]

        # _dataset_key format should be GAMEID_YYYYMMDD_to_YYYYMMDD
        for _key in _game_datasets:
            _dataset_key = DatasetKey(_key, sanitizedRequestParams.GameID)
            if _dataset_key.IsValid:

                # If this is the first range block in our loop, or this range block has an earlier year than our first_year
                if "first_year" not in file_info or file_info["first_year"] > _dataset_key.FromYear:
                    file_info["first_year"] = _dataset_key.FromYear
                    file_info["first_month"] = _dataset_key.FromMonth

                # If this is range is for the same year but an earlier month
                elif file_info["first_year"] == _dataset_key.FromYear and file_info["first_month"] > _dataset_key.FromMonth:
                    file_info["first_month"] = _dataset_key.FromMonth

                # If this is the first range block, or this range block has a later year than the last_year
                if "last_year" not in file_info or file_info["last_year"] < _dataset_key.ToYear:
                    file_info["last_year"] = _dataset_key.ToYear
                    file_info["last_month"] = _dataset_key.ToMonth

                # If this is range is for the same year but with a later month
                elif file_info["last_year"] == _dataset_key.ToYear \
                 and file_info["last_month"] < _dataset_key.ToMonth:
                    file_info["last_month"] = _dataset_key.ToMonth

                # If a month & year wasn't actually given and this is the last range
                # OR if this range contains the given year & month
                if ((sanitizedRequestParams.Year is None and sanitizedRequestParams.Month is None and _dataset_key == _last_dataset_key) 
                    or (sanitizedRequestParams.Year >= _dataset_key.FromYear and sanitizedRequestParams.Month >= _dataset_key.FromMonth and sanitizedRequestParams.Year <= _dataset_key.ToYear and sanitizedRequestParams.Month <= _dataset_key.ToMonth)):
                    # Base URLs
                    FILEHOST_BASE_URL   : str = file_list_json.get("CONFIG", {}).get("files_base")
                    TEMPLATES_BASE_URL  : str = file_list_json.get("CONFIG", {}).get("templates_base")
                    CODESPACES_BASE_URL : str = "https://codespaces.new/opengamedata/opengamedata-samples/tree/"
                    GITHUB_BASE_URL     : str = "https://github.com/opengamedata/opengamedata-core/tree/"

                    _branch_name = sanitizedRequestParams.GameID.lower().replace('_', '-')
                    _dataset_json = file_list_json.get(sanitizedRequestParams.GameID, {}).get(_dataset_key, {})
                    _revision    = _dataset_json.get("ogd_revision") or None
                
                    # Files
                    file_info["raw_file"]        = FILEHOST_BASE_URL + _dataset_json.get("raw_file", None)        if "raw_file"        in _dataset_json else None
                    file_info["events_file"]     = FILEHOST_BASE_URL + _dataset_json.get("events_file", None)     if "events_file"     in _dataset_json else None
                    file_info["sessions_file"]   = FILEHOST_BASE_URL + _dataset_json.get("sessions_file", None)   if "sessions_file"   in _dataset_json else None
                    file_info["players_file"]    = FILEHOST_BASE_URL + _dataset_json.get("players_file", None)    if "players_file"    in _dataset_json else None
                    file_info["population_file"] = FILEHOST_BASE_URL + _dataset_json.get("population_file", None) if "population_file" in _dataset_json else None

                    # Templates
                    file_info["events_template"]     = TEMPLATES_BASE_URL + _dataset_json.get("events_template", None)     if "events_template"     in _dataset_json else None
                    file_info["sessions_template"]   = TEMPLATES_BASE_URL + _dataset_json.get("sessions_template", None)   if "sessions_template"   in _dataset_json else None
                    file_info["players_template"]    = TEMPLATES_BASE_URL + _dataset_json.get("players_template", None)    if "players_template"    in _dataset_json else None
                    file_info["population_template"] = TEMPLATES_BASE_URL + _dataset_json.get("population_template", None) if "population_template" in _dataset_json else None

                    file_info["events_codespace"]   = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json"
                    file_info["sessions_codespace"] = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fplayer-template%2Fdevcontainer.json"
                    file_info["players_codespace"]  = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fsession-template%2Fdevcontainer.json"

                    # Convention for branch naming is lower-case with dashes,
                    # while game IDs are usually upper-case with underscores, so make sure we do the conversion
                    file_info["detectors_link"] = f"{GITHUB_BASE_URL}{_revision}/games/{_branch_name}/detectors" if _revision else None
                    file_info["features_link"]  = f"{GITHUB_BASE_URL}{_revision}/games/{_branch_name}/features"  if _revision else None
                    
                    found_matching_range = True
            else:
                pass # leave `found_matching_range` as false

        if not found_matching_range:
            file_info["found_matching_range"] = False
            file_info["events_file"] = None
            file_info["players_file"] = None
            file_info["population_file"] = None
            file_info["raw_file"] = None
            file_info["sessions_file"] = None
            file_info["events_template"] = None
            file_info["players_template"] = None
            file_info["population_template"] = None
            file_info["sessions_template"] = None
            file_info["detectors_link"] = None
            file_info["features_link"] = None
        else:
            file_info["found_matching_range"] = True

    return APIResponse(True, file_info).ToDict()

