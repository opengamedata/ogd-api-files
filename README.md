# opengamedata-api-files

This is the backend api used by https://github.com/opengamedata/opengamedata-website

# Getting Started:

## Running the app locally via the development Flask server:

Steps to run:

1. Ensure you have Python and pip installed in your development environment.
2. From the app's root directory run `pip install -r requirements.txt` to ensure you have Flask and other dependencies installed for the app.
3. If you don't have a config/config.py file for local development, copy config/config.py.template to config/config.py to create one. Populate config.py with secret values as needed.
4. Run `flask run` or `flask run --debug`.
5. A web server should be running at http://localhost:5000

# API endpoints:

`/getGameUsageByMonth`
Query string params: game_id, year, month

`/getGameFileInfoByMonth`
Query string params: game_id, year, month
