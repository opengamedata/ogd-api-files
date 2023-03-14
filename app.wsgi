import sys
import os

# Ensure this path is writable by the user the WSGI daemon runs as
os.environ['OGD_FLASK_APP_LOG_FILE'] = '/var/log/flask-apps/ogd-website-api.log'

# Specifying the path used in the hosting environment, there might be a better way to do this
if not "/var/www/wsgi-bin" in sys.path:
    sys.path.append("/var/www/wsgi-bin")
from app import application
