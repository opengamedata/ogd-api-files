# import standard libraries
import json
import zipfile
from io import BytesIO
from typing import Optional
from urllib import error as url_error
from urllib import request as url_request

# import 3rd-party libraries
import pandas as pd
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

# import local files
from apis.configs.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams
from utils.utils import GetFileList, MatchDatasetRequest


class DatasetFile(Resource):
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
                cfg           : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
                file_list     : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
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
