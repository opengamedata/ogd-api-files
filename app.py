# import standard libraries
import sys, os, re, datetime, urllib, json
from logging.config import dictConfig
from calendar import monthrange

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

# If a dedicated log file is defined for this Flask app, we'll also log there
# Ensure this is in a directory writable by the user executing the WSGI app (likely the web daemon - www-data or apache)
if "OGD_FLASK_APP_LOG_FILE" in os.environ:
    logHandlers['wsgi_app_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ["OGD_FLASK_APP_LOG_FILE"],
            'maxBytes': 100000000, # 100 MB
            'backupCount': 10, # Up to 10 rotated files
            'formatter': 'default'
    }

    logRootHandlers.append('wsgi_app_file')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': logHandlers,
    'root': {
        'level': 'INFO',
        'handlers': logRootHandlers
    }
})

application = Flask(__name__)

# Allow cross-origin requests from any origin by default
# This presents minimal risk to visitors since the API merely retrieves non-sensitive data
CORS(application)

# TODO: Now that logging is set up, import our local config settings
from config.config import settings
application.logger.setLevel(settings['DEBUG_LEVEL'])

# Shared utility function to retrieve game_id, year, and month from the request's query string.
# Defaults are used if a value was not given or is invalid
def getSanitizedQueryParams():

    now_date = datetime.date.today()

    # Extract query string parameters
    game_id = request.args.get("game_id", default = "", type=str)
    year = request.args.get("year", default=now_date.year, type=int)
    month = request.args.get("month", default=now_date.month, type=int)
    
    # Sanitize values from query string
    if re.search("^[A-Za-z]+$", game_id) is None:
        game_id = ""

    game_id = game_id.upper()

    if month < 1 or month > 12:
        month = now_date.month

    if year < 2000 or year > now_date.year:
        year = now_date.year

    return { "game_id": game_id, "year": year, "month": month }

# Get game usage statistics for a given game, year, and month
@application.route('/getGameUsageByMonth', methods=['GET'])
def get_game_usage_by_month():

    sanitizedInput = getSanitizedQueryParams()

    if sanitizedInput["game_id"] is None or sanitizedInput["game_id"] == "":
        return APIResponse(False, None).ToDict()

    # If we don't have a mapping for the given game
    if not sanitizedInput["game_id"] in settings["BIGQUERY_GAME_MAPPING"]:
        return APIResponse(False, None).ToDict()

    total_monthly_sessions = 0
    sessions_by_day = {}

    bqInterface = BigQueryInterface(settings["BIGQUERY_GAME_MAPPING"][sanitizedInput["game_id"]])
    total_monthly_sessions = bqInterface.GetTotalSessionsForMonth(sanitizedInput["year"], sanitizedInput["month"])
    sessions_by_day = bqInterface.GetSessionsPerDayForMonth(sanitizedInput["year"], sanitizedInput["month"])

    responseObj = {
        "game_id": sanitizedInput["game_id"],
        "selected_month": sanitizedInput["month"],
        "selected_year": sanitizedInput["year"],
        "total_monthly_sessions": total_monthly_sessions,
        "sessions_by_day": sessions_by_day
    }

    return APIResponse(True, responseObj).ToDict()

# Get info on the files that are available for the given game in the given month & year
@application.route('/getGameFileInfoByMonth', methods=['GET'])
def get_game_file_info_by_month():

    sanitizedInput = getSanitizedQueryParams()

    file_list_url = 'https://opengamedata.fielddaylab.wisc.edu/data/file_list.json'

    file_list_response = urllib.request.urlopen(file_list_url)
    file_list_json = json.loads(file_list_response.read())

    # If we couldn't find the given game in file_list.json, or the game didn't have any date ranges
    if not sanitizedInput["game_id"] in file_list_json or len(file_list_json[sanitizedInput["game_id"]]) == 0:
        return APIResponse(False, None).ToDict()

    file_info = {}
    files_base_url = file_list_json["CONFIG"]["files_base"]
    templates_base_url = file_list_json["CONFIG"]["templates_base"]
    found_matching_range = False

    # None of the paths in file_list.json are populated yet, so default to the base URL which is the Github repo root
    # TODO: Remove this when we get non-null entries
    file_info["events_template"] = templates_base_url
    file_info["players_template"] = templates_base_url
    file_info["population_template"] = templates_base_url
    file_info["sessions_template"] = templates_base_url

   # If a year and month wasn't given, we'll default to returning files & info for the last range
    if request.args.get("year") is None and request.args.get("month") is None:
        lastRangeKey = list(file_list_json[sanitizedInput["game_id"]])[-1]

    # rangeKey format is GAMEID_YYYYMMDD_to_YYYYMMDD
    for rangeKey in file_list_json[sanitizedInput["game_id"]]:
            
        rangeKeyParts = rangeKey.split("_")
        
        # If this rangeKey matches the expected format
        if len(rangeKeyParts) == 4:
            fromYear = int(rangeKeyParts[1][0:4])
            fromMonth = int(rangeKeyParts[1][4:6])
            toYear = int(rangeKeyParts[3][0:4])
            toMonth = int(rangeKeyParts[3][4:6])

            # If this is the first range block in our loop, or this range block has an earlier year than our first_year
            if "first_year" not in file_info or file_info["first_year"] > fromYear:

                file_info["first_year"] = fromYear
                file_info["first_month"] = fromMonth

            # If this is range is for the same year but an earlier month
            elif file_info["first_year"] == fromYear and file_info["first_month"] > fromMonth:

                file_info["first_month"] = fromMonth

            # If this is the first range block, or this range block has a later year than the last_year
            if "last_year" not in file_info or file_info["last_year"] < toYear:

                file_info["last_year"] = toYear
                file_info["last_month"] = toMonth

            # If this is range is for the same year but with a later month
            elif file_info["last_year"] == toYear and file_info["last_month"] < toMonth:

                file_info["last_month"] = toMonth

            # If a month & year wasn't actually given and this is the last range
            # OR if this range contains the given year & month
            if ((request.args.get("year") is None and request.args.get("month") is None and rangeKey == lastRangeKey) 
                or (sanitizedInput["year"] >= fromYear and sanitizedInput["month"] >= fromMonth and sanitizedInput["year"] <= toYear and sanitizedInput["month"] <= toMonth)):
              
                # Files
                file_info["events_file"] = files_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["events_file"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["events_file"] else None
                file_info["players_file"] = files_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["players_file"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["players_file"] else None
                file_info["population_file"] = files_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["population_file"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["population_file"] else None
                file_info["raw_file"] = files_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["raw_file"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["raw_file"] else None
                file_info["sessions_file"] = files_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["sessions_file"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["sessions_file"] else None

                # Templates
                # TODO: Uncomment this section when we have non-null values in file_list.json
                #file_info["events_template"] = templates_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["events_template"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["events_template"] else None
                #file_info["players_template"] = templates_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["players_template"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["players_template"] else None
                #file_info["population_template"] = templates_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["population_template"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["population_template"] else None
                #file_info["sessions_template"] = templates_base_url + file_list_json[sanitizedInput["game_id"]][rangeKey]["sessions_template"] if file_list_json[sanitizedInput["game_id"]][rangeKey]["sessions_template"] else None
                
                found_matching_range = True

    if not found_matching_range:
        file_info["found_matching_range"] = False
        file_info["events_file"] = None
        file_info["players_file"] = None
        file_info["population_file"] = None
        file_info["raw_file"] = None
        file_info["sessions_file"] = None
        # TODO: Uncomment this section when we have non-null values in file_list.json
        #file_info["events_template"] = None
        #file_info["players_template"] = None
        #file_info["population_template"] = None
        #file_info["sessions_template"] = None
    else:
        file_info["found_matching_range"] = True

    return APIResponse(True, file_info).ToDict()

