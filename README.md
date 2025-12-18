# opengamedata-api-files

This is the OpenGameData dataset/file repository API.

Its primary use is for getting information about what data is available from the fileserver used by [opengamedata.fielddaylab.wisc.edu](opengamedata.fielddaylab.wisc.edu), but could be used for any repository of datasets using the OpenGameData pipeline.

## API endpoints

The latest release of the API supports the endpoints listed below.
Experimental endpoints that have not yet been included in a release but are intended for inclusion in future versions are labeled as such.

Broadly speaking, the file API has a 3-level hierarchy of data about game datasets.

1. Games: The top-level entity is a game. Each game has an ID and is associated with one or more datasets.
2. Datasets: The term "dataset" refers to all data for a specific month of play from a specific game.
  For any given dataset, the actual data in that "set" may include game events, post-hoc "detector" events, session-level features, player-level features, or population-level features.
3. Files: A "file" contains actual data of one type from a dataset.

### Game-Level Endpoints

* `/games` (experimental/upcoming)  

  Retrieve a list of all games for which at least one dataset exists.

* `/games/<game_id>` (experimental/upcoming)  

  Retrieve a summary of the game and its datasets

  Example:
  ```bash
  curl https://ogd-staging.fielddaylab.wisc.edu/path/to/app.wsgi/games/AQUALAB
  ```

  ```json
  response = {
    "type": "GET",
    "val": {
      "game_id": "AQUALAB",
      "dataset_count": 57,
      "initial_dataset": "2021-04-11 00:00:00"
    },
    "msg": "SUCCESS: Retrieved monthly game usage"
  }
  ```

### Dataset-Level Endpoints

* `/games/<game_id>/datasets` (experimental/upcoming)  

  Retrieve a list of datasets and associated session counts for a specific game.

  Approximately equivalent to the `/MonthlyGameUsage` legacy endpoint.
  However, the legacy endpoint includes additional entries for non-existent datasets that lie within the range of all extant datasets, with the session counts set to 0.

  Example:
  ```bash
  curl https://ogd-staging.fielddaylab.wisc.edu/path/to/app.wsgi/games/AQUALAB/datasets
  ```

  ```json
  response = {
    "type": "GET",
    "val": {
      "game_id": "AQUALAB",
      "datasets": [
        ...
        {"year": 2025, "month": 9, "total_sessions": 4908},
        {"year": 2025, "month": 10, "total_sessions": 4763},
        {"year": 2025, "month": 11, "total_sessions": 5339}
      ]
    },
    "msg": "SUCCESS: Retrieved monthly game usage"
  }
  ```

* `/games/<game_id>/datasets/<year>` (experimental/upcoming)

  Retrieve a list of datasets and associated session counts for a specific game within a specific month.
  Roughly equivalent to the `/games/<game_id>/datasets/` endpoint, but scoped to a single year.

  Example:
  ```bash
  curl https://ogd-staging.fielddaylab.wisc.edu/path/to/app.wsgi/games/AQUALAB/datasets/2023
  ```

  ```json
  response = {
    "type": "GET",
    "val": {
      "game_id": "AQUALAB",
      "datasets": [
        {"year": 2023, "month": 1, "total_sessions": 2013},
        {"year": 2023, "month": 2, "total_sessions": 17},
        {"year": 2023, "month": 3, "total_sessions": 8605}
        ...
      ]
    },
    "msg": "SUCCESS: Retrieved monthly game usage"
  }
  ```

* `/games/<game_id>/datasets/<year>/<month>` (experimental/upcoming)

  Get detailed info on the files and other resources that are available for a specific dataset. This is roughly equivalent to the `/getGameFileInfoByMonth` legacy endpoint.

### File-Level Endpoints

* `/games/<game_id>/datasets/<month>/<year>/<file_type>` (experimental/upcoming)

  Retrieve the contents of a specific dataset file. Valid `file_type`s are `population`, `player`, and `session`.

### Legacy Endpoints

Endpoints used by the OpenGameData website, which use an outdated convention.
We intend to deprecate these in the near future.

* `/MonthlyGameUsage` : Retrieve a list of datasets and associated session counts for a specific game.

  Query string params: `game_id`

* `/getGameFileInfoByMonth` : Get detailed info on the files and other resources that are available for a specific dataset.

  Query string params: `game_id`, `year`, `month`

## Developer Instructions

### Running the app locally via the development Flask server

Steps to run:

1. Ensure you have Python and pip installed in your development environment.
2. From the app's root directory run `pip install -r requirements.txt` to ensure you have Flask and other dependencies installed for the app.
3. If you don't have a config/config.py file for local development, copy config/config.py.template to config/config.py to create one. Populate config.py with secret values as needed.
4. Run `flask run` or `flask run --debug`.
5. A web server should be running at http://localhost:5000
