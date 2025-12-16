# import standard libraries
import json
import zipfile
from datetime import date, timedelta
from io import BytesIO
from typing import Any, Dict, Optional
from urllib import error as url_error
from urllib import request as url_request

# import 3rd-party libraries
import pandas as pd
from flask import Flask, current_app
from flask_restful import Resource, Api

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

# import local files
from apis.resources.GameList import GameList
from apis.resources.DatasetList import DatasetList
from apis.configs.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams
from utils.utils import GetFileList, MatchDatasetRequest

class FileAPI:
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
        api.add_resource(GameList,    '/games/list')
        api.add_resource(DatasetList, '/games/<game_id>/datasets/list')
        api.add_resource(FileAPI.GameDatasetInfo,  '/games/<game_id>/datasets/<month>/<year>/files/')
        api.add_resource(FileAPI.DataFile,  '/games/<game_id>/datasets/<month>/<year>/files/<file_type>')
        FileAPI.server_config = settings

    class GameDatasetInfo(Resource):
        """
        Get info on the files that are available for the given game in the given month & year

        Inputs:
        - Game ID
        - Year
        - Month
        Outputs:
        - DatasetSchema of most recently-exported dataset for game in month
        """
        def get(self, game_id, month, year):
            ret_val = APIResponse.Default(req_type=RESTType.GET)

            try:
                sanitary_params = SanitizedParams.FromParams(game_id=game_id, year=year, month=month)

            # 1. Get the list of datasets available on the server, for given game.
                if sanitary_params:
                    file_list     : DatasetRepositoryConfig = GetFileList(FileAPI.server_config.FileListURL)
                    game_datasets : DatasetCollectionSchema = file_list.Games.get(sanitary_params.GameID or "NO GAME REQUESTED", DatasetCollectionSchema.Default())

                    # If we couldn't find the requested game in file_list.json, or the game didn't have any date ranges, skip.
                    if (sanitary_params.GameID is None):
                        ret_val.RequestErrored(msg=f"Bad GameID '{sanitary_params.GameID}'")
                        return ret_val.AsFlaskResponse
                    elif (len(game_datasets.Datasets) == 0):
                        ret_val.RequestErrored(msg=f"GameID '{sanitary_params.GameID}' has no available datasets", status=ResponseStatus.ERR_NOTFOUND)
                        return ret_val.AsFlaskResponse
                else:
                    raise ValueError("Could not process inputs!")
            except Exception as err:
                current_app.logger.error(f"{type(err)} error processing request inputs:\n{err}")
                ret_val.ServerErrored("Unexpected error processing request inputs.")
            else:
            # 2. Search for the most recently modified dataset that contains the requested month and year
                _matched_dataset : Optional[DatasetSchema] = MatchDatasetRequest(sanitary_request=sanitary_params, available_datasets=game_datasets)

                if _matched_dataset:
                    if _matched_dataset.Key.DateFrom and _matched_dataset.Key.DateTo:
                        file_info = {}

                        # If this range contains the given year & month
                        # Base URLs
                        CODESPACES_BASE_URL : str = "https://codespaces.new/opengamedata/opengamedata-samples/tree/"
                        GITHUB_BASE_URL     : str = "https://github.com/opengamedata/opengamedata-core/tree/"
                        
                        # Date information
                        file_info["first_year"]  = _matched_dataset.Key.DateFrom.year
                        file_info["first_month"] = _matched_dataset.Key.DateFrom.month
                        file_info["last_year"]   = _matched_dataset.Key.DateTo.year
                        file_info["last_month"]  = _matched_dataset.Key.DateTo.month
                        _branch_name     = sanitary_params.GameID.lower().replace('_', '-')
                        _revision        = _matched_dataset.OGDRevision or None

                        # Files
                        file_info["raw_file"]        = f"{file_list.RemoteURL}{_matched_dataset.GameEventsFile}" if _matched_dataset.GameEventsFile is not None else None
                        file_info["events_file"]     = f"{file_list.RemoteURL}{_matched_dataset.AllEventsFile}"  if _matched_dataset.AllEventsFile  is not None else None
                        file_info["sessions_file"]   = f"{file_list.RemoteURL}{_matched_dataset.SessionsFile}"   if _matched_dataset.SessionsFile   is not None else None
                        file_info["players_file"]    = f"{file_list.RemoteURL}{_matched_dataset.PlayersFile}"    if _matched_dataset.PlayersFile    is not None else None
                        file_info["population_file"] = f"{file_list.RemoteURL}{_matched_dataset.PopulationFile}" if _matched_dataset.PopulationFile is not None else None

                        # Templates
                        file_info["events_template"]     = f"{file_list.TemplatesBase}{_matched_dataset.EventsTemplate}"     if _matched_dataset.EventsTemplate     is not None else None
                        file_info["sessions_template"]   = f"{file_list.TemplatesBase}{_matched_dataset.SessionsTemplate}"   if _matched_dataset.SessionsTemplate   is not None else None
                        file_info["players_template"]    = f"{file_list.TemplatesBase}{_matched_dataset.PlayersTemplate}"    if _matched_dataset.PlayersTemplate    is not None else None
                        file_info["population_template"] = f"{file_list.TemplatesBase}{_matched_dataset.PopulationTemplate}" if _matched_dataset.PopulationTemplate is not None else None

                        file_info["events_codespace"]   = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json"
                        file_info["sessions_codespace"] = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fplayer-template%2Fdevcontainer.json"
                        file_info["players_codespace"]  = f"{CODESPACES_BASE_URL}{_branch_name}?quickstart=1&devcontainer_path=.devcontainer%2Fsession-template%2Fdevcontainer.json"

                        # Convention for branch naming is lower-case with dashes,
                        # while game IDs are usually upper-case with underscores, so make sure we do the conversion
                        file_info["detectors_link"] = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{sanitary_params.GameID.upper()}/detectors" if _revision else None
                        file_info["features_link"]  = f"{GITHUB_BASE_URL}{_revision}/src/ogd/games/{sanitary_params.GameID.upper()}/features"  if _revision else None
                        file_info["found_matching_range"] = True

                        ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=file_info)
                    else:
                        _msg = f"Dataset key {_matched_dataset.Key} was invalid." if _matched_dataset else "No datasets found!"
                        ret_val.RequestErrored(msg=_msg)
                else:
                    ret_val.RequestErrored(msg=f"Could not find a dataset for {sanitary_params.GameID} in {sanitary_params.Month:>02}/{sanitary_params.Year:>04}", status=ResponseStatus.ERR_NOTFOUND)

            return ret_val.AsFlaskResponse

    class DataFile(Resource):
        """
        Get the specific requested file

        Inputs:
        - Game ID
        - Year
        - Month
        Outputs:
        - DatasetSchema of most recently-exported dataset for game in month
        """
        def get(self, game_id, month, year, file_type):
            ret_val = APIResponse.Default(req_type=RESTType.GET)

            try:
                sanitary_params = SanitizedParams.FromParams(game_id=game_id, year=year, month=month)

            # 1. Get the list of datasets available on the server, for given game.
                if sanitary_params:
                    file_list     : DatasetRepositoryConfig = GetFileList(FileAPI.server_config.FileListURL)
                    game_datasets : DatasetCollectionSchema = file_list.Games.get(sanitary_params.GameID or "NO GAME REQUESTED", DatasetCollectionSchema.Default())

                    # If we couldn't find the requested game in file_list.json, or the game didn't have any date ranges, skip.
                    if (sanitary_params.GameID is None):
                        ret_val.RequestErrored(msg=f"Bad GameID '{sanitary_params.GameID}'")
                        return ret_val.AsFlaskResponse
                    elif (len(game_datasets.Datasets) == 0):
                        ret_val.ServerErrored(msg=f"GameID '{sanitary_params.GameID}' did not have available datasets")
                        return ret_val.AsFlaskResponse
                else:
                    raise ValueError("Could not process inputs!")
            except Exception as err:
                current_app.logger.error(f"{type(err)} error processing request inputs:\n{err}")
                ret_val.ServerErrored("Unexpected error processing request inputs.")
            else:
            # 2. Search for the most recently modified dataset that contains the requested month and year
                try:
                    _matched_dataset : Optional[DatasetSchema] = MatchDatasetRequest(sanitary_request=sanitary_params, available_datasets=game_datasets)

                    if _matched_dataset:
                        if _matched_dataset.Key.DateFrom and _matched_dataset.Key.DateTo:
                            file_link = None
                            missing_file_msg = f"Dataset for {game_id} from {f'{month:02}/{year:04}'} was not found."
                            match str(file_type).upper():
                                case "SESSION":
                                    file_link = f"{file_list.RemoteURL}{_matched_dataset.SessionsFile.as_posix()}"   if _matched_dataset.SessionsFile   is not None else None
                                case "PLAYER":
                                    file_link = f"{file_list.RemoteURL}{_matched_dataset.PlayersFile.as_posix()}"    if _matched_dataset.PlayersFile    is not None else None
                                case "POPULATION":
                                    file_link = f"{file_list.RemoteURL}{_matched_dataset.PopulationFile.as_posix()}" if _matched_dataset.PopulationFile is not None else None
                                case "EVENT":
                                    missing_file_msg="Event files are not yet supported."
                                case _:
                                    missing_file_msg=f"Unrecognized file type {file_type}."
                            if file_link:
                                datafile_response = url_request.urlopen(file_link)
                                with zipfile.ZipFile(BytesIO(datafile_response.read())) as zipped:
                                    for f_name in zipped.namelist():
                                        if f_name.endswith(".tsv"):
                                            data = pd.read_csv(zipped.open(f_name), sep="\t").replace({float('nan'):None})
                                            data = self._secondaryParse(data)
                                            result = {
                                                "columns": list(data.columns),
                                                "rows": list(data.apply(lambda series : series.to_dict(), axis=1))
                                            }
                                            ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=result)
                            else:
                                ret_val.RequestErrored(msg=missing_file_msg)
                        else:
                            ret_val.RequestErrored(msg=f"Dataset key {_matched_dataset.Key} was invalid.")
                    else:
                        ret_val.RequestErrored(msg=f"Could not find a dataset for {sanitary_params.GameID} in {sanitary_params.Month:>02}/{sanitary_params.Year:>04}", status=ResponseStatus.ERR_NOTFOUND)
                except url_error.HTTPError as err:
                    current_app.logger.error(f"HTTP error getting {file_type} file from {file_link}:\n{err}")
                    ret_val.ServerErrored(msg=f"Server experienced an error retrieving {file_type} file from {f'{sanitary_params.Month:>02}/{sanitary_params.Year:>04}'} for {sanitary_params.GameID}.")
                except Exception as err:
                    current_app.logger.error(f"Uncaught {type(err)} getting {file_type} file from {file_link}:\n{err}\n{err.__traceback__}")
                    ret_val.ServerErrored(msg=f"Server experienced an error retrieving {file_type} file from {f'{sanitary_params.Month:>02}/{sanitary_params.Year:>04}'} for {sanitary_params.GameID}.")

            return ret_val.AsFlaskResponse

        @staticmethod
        def _secondaryParse(df:pd.DataFrame) -> pd.DataFrame:
            json_cols = [col for col in df.select_dtypes("object").columns if set(map(type, df[col])) == {str} and df[col].iloc[0][0] in {"[", "{"}]
            for col in json_cols:
                try:
                    df[col] = df[col].apply(json.loads)
                except json.decoder.JSONDecodeError as err:
                    current_app.logger.debug(f"Column {col} was identified as JSON-format, but could not be parsed:\n{err}")
            df = df.astype({col:"object" for col in df.select_dtypes("int64").columns})
            df = df.astype({col:"object" for col in df.select_dtypes("bool").columns})

            return df

