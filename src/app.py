# import standard libraries
import logging

# import 3rd-party libraries
from flask import Flask
from flask_cors import CORS

# import ogd libraries
from ogd.common.utils.Logger import Logger

# import local files
from config.config import settings

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
application.logger.setLevel(settings['DEBUG_LEVEL'])

def _logImportErr(msg:str, err:Exception):
    application.logger.warning(msg)
    application.logger.exception(err)
Logger.InitializeLogger(level=logging.INFO, use_logfile=False)


try:
    from apis.LegacyWebAPI import LegacyWebAPI
except ImportError as err:
    _logImportErr(msg="Could not import Legacy Web API:", err=err)
except Exception as err:
    _logImportErr(msg="Could not import Legacy Web API, general error:", err=err)
else:
    LegacyWebAPI.register(application, settings=settings)
