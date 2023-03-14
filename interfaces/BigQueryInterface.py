import os
from calendar import monthrange
from google.cloud import bigquery
from typing import Dict

class BigQueryInterface:

    # We're expecting a config structure for a specific game to be passed to the constructor:
    # {"PROJECT_ID":"aqualab-57f88", "DATASET_ID":"analytics_271167280", "TABLE_PREFIX":"events_*", "CREDENTIALS_PATH":"./config/aqualab.json", "SCHEMA_TYPE": "EVENTS-FIREBASE"}
    def __init__(self, config):

        self._config = config

        # The BigQuery client expects our credential filepath to be defined in os.environ["GOOGLE_APPLICATION_CREDENTIALS"], do that now
        if "GITHUB_ACTIONS" not in os.environ:
            # Assumes the current file is in a directory one level below the app's root
            APP_ROOT = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..')
            # Assumes the path specified in CREDENTIALS_PATH is a relative path from the app root
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(APP_ROOT, self._config["CREDENTIALS_PATH"])

        self._client: bigquery.Client = bigquery.Client()

    # Get the total number of sessions for a given month
    def GetTotalSessionsForMonth(self, year: int, month: int) -> int:

        # Determine how many days are in the given month for the given year
        weekDayOfFirstDay, numDaysInMonth = monthrange(year, month)
        
        # Example: `aqualab-57f88.analytics_271167280.events_*`
        fqTableIdWildcard = self._config["PROJECT_ID"] + "." + self._config["DATASET_ID"] + "." + self._config["TABLE_PREFIX"]

        # If this game's events are logged using the Firebase table schema
        if self._config["SCHEMA_TYPE"] == "EVENTS-FIREBASE":

            query = "SELECT COUNT(DISTINCT(session_id)) mycount"
            query += " FROM (SELECT param_session.value.int_value as session_id FROM `" + fqTableIdWildcard + "` CROSS JOIN UNNEST(event_params) AS param_session"
            query += " WHERE _TABLE_SUFFIX BETWEEN '" + str(year) + str(month).zfill(2) + "01' AND '" + str(year) + str(month).zfill(2) + str(numDaysInMonth) + "')"

        else:
            raise "Unsupported schema type"

        job = self._client.query(query)

        for row in job:
            return row["mycount"] # row values can be accessed by index [0] or field name

    # Get the total number of sessions for each day in a given month
    def GetSessionsPerDayForMonth(self, year: int, month: int) -> Dict[str, int]:

        # Determine how many days are in the given month for the given year
        weekDayOfFirstDay, numDaysInMonth = monthrange(year, month)
        
        fqTableIdWildcard = self._config["PROJECT_ID"] + "." + self._config["DATASET_ID"] + "." + self._config["TABLE_PREFIX"]

        # If this game's events are logged using the Firebase table schema
        if self._config["SCHEMA_TYPE"] == "EVENTS-FIREBASE":

            query = "SELECT COUNT(DISTINCT(session_id)) mycount, _TABLE_SUFFIX"
            query += " FROM (SELECT param_session.value.int_value AS session_id, _TABLE_SUFFIX FROM `" + fqTableIdWildcard + "` CROSS JOIN UNNEST(event_params) AS param_session"
            query += " WHERE _TABLE_SUFFIX BETWEEN '" + str(year) + str(month).zfill(2) + "01' AND '" + str(year) + str(month).zfill(2) + str(numDaysInMonth) + "')"
            query += " GROUP BY _TABLE_SUFFIX ORDER BY _TABLE_SUFFIX"

        else:
            raise "Unsupported schema type"

        job = self._client.query(query)

        resultsPerDay = {}

        # Loop through each day that had sessions
        for row in job:

            # YYYYMMDD 
            # Get the date characters
            dayOfMonth = row["_TABLE_SUFFIX"][6:8]
            
            # Trim off leading zero
            if dayOfMonth.startswith("0"):
                dayOfMonth = dayOfMonth[1:2]

            # Day Of Month -> Num Sessions
            resultsPerDay[dayOfMonth] = row["mycount"]
        

        # Loop through each day in the month to ensure we have placeholder zero counts
        sessions_by_day = {}
        
        for dayOfMonth in range(1, numDaysInMonth + 1):

            sessions_by_day[str(dayOfMonth)] = 0

            if str(dayOfMonth) in resultsPerDay:
                sessions_by_day[str(dayOfMonth)] = resultsPerDay[str(dayOfMonth)]
        

        return sessions_by_day
