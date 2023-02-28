# import standard libraries
import sys, os, re, datetime, urllib, json
from logging.config import dictConfig

# import 3rd-party libraries
from flask import Flask, send_file, request
from flask_cors import CORS

# import our app libraries
from models.APIResponse import APIResponse

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
# from config.config import settings
# application.logger.setLevel(settings['DEBUG_LEVEL'])

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
    

    # TODO: If game_id isn't empty, query the database with the given criteria
    # Code should go in a BigQueryInterface

    responseObj = {
        "game_id": sanitizedInput["game_id"],
        "selected_month": sanitizedInput["month"],
        "selected_year": sanitizedInput["year"],
        "first_month": 3,
        "first_year": 2020,
        "last_month": 2,
        "last_year": 2023,
        "total_monthly_sessions": 235235,
        "sessions_by_day": {
            1: 34,
            2: 6034,
            3: 0,
            4: 3333
        }
    }

    return APIResponse(True, responseObj).ToDict()

# Get info on the files that are available for the given game in the given month & year
@application.route('/getGameFileInfoByMonth', methods=['GET'])
def get_game_file_info_by_month():

    sanitizedInput = getSanitizedQueryParams()

    file_list_url = 'https://opengamedata.fielddaylab.wisc.edu/data/file_list.json'

    file_list_response = urllib.request.urlopen(file_list_url)
    file_list_json = json.loads(file_list_response.read())

    if not sanitizedInput["game_id"] in file_list_json:
        return APIResponse(False, None).ToDict()

    file_info = None

    # rangeKey format is GAMEID_YYYYMMDD_to_YYYYMMDD
    for rangeKey in file_list_json[sanitizedInput["game_id"]]:
      
        rangeKeyParts = rangeKey.split("_")
        
        # If this rangeKey matches the expected format
        if len(rangeKeyParts) == 4:
            fromYear = int(rangeKeyParts[1][0:4])
            fromMonth = int(rangeKeyParts[1][4:6])
            toYear = int(rangeKeyParts[3][0:4])
            toMonth = int(rangeKeyParts[3][4:6])

            # If the given date is within the range
            if sanitizedInput["year"] >= fromYear and sanitizedInput["month"] >= fromMonth and sanitizedInput["year"] <= toYear and sanitizedInput["month"] <= toMonth:
                # Use this file info
                file_info = file_list_json[sanitizedInput["game_id"]][rangeKey]
                break

    # TODO: Determine the response structure we need for the frontend

    if file_info is None:
        return APIResponse(False, None).ToDict()

    return APIResponse(True, file_info).ToDict()

