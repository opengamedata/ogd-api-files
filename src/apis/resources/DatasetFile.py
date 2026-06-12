# import standard libraries
import dataclasses
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
from ogd.apis.models.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.apis.models.files.DatasetFile import DatasetFile as DatasetFileModel
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from utils.SanitizedParams import SanitizedParams
from utils.utils import GetFileList, FindDataset


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

        safe_game_id  = SanitizedParams.SanitizeGameID(game_id=game_id)
        safe_year     = SanitizedParams.SanitizeYear(year=year)
        safe_month    = SanitizedParams.SanitizeMonth(month=month)
        safe_filetype = SanitizedParams.SanitizeFileType(file_type=file_type)

        # 1. Get the list of datasets available on the server, for given game.
        if safe_game_id and safe_year and safe_month and safe_filetype:
            try:
                cfg             : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
                file_list       : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
                matched_dataset : Optional[DatasetSchema] = FindDataset(game_id=safe_game_id, year=safe_year, month=safe_month, available_datasets=file_list.Games)

            # 2. Search for the most recently modified dataset that contains the requested month and year

                if matched_dataset and matched_dataset.Key.DateFrom and matched_dataset.Key.DateTo:
                    if file_list.RemoteURL is not None:
                        matched_dataset.BaseFileLocation = file_list.RemoteURL

                    file_link = None
                    missing_file_msg = f"Dataset for {game_id} from {f'{month:02}/{year:04}'} was not found."
                    match str(file_type).upper():
                        case "SESSION":
                            file_link = matched_dataset.SessionsFile(relative=False)
                        case "PLAYER":
                            file_link = matched_dataset.PlayersFile(relative=False)
                        case "POPULATION":
                            file_link = matched_dataset.PopulationFile(relative=False)
                        case "EVENT":
                            missing_file_msg="Event files are not yet supported."
                        case _:
                            missing_file_msg=f"Unrecognized file type {file_type}."
                    if file_link:
                        datafile_response = url_request.urlopen(file_link)
                        with zipfile.ZipFile(BytesIO(datafile_response.read())) as zipped:
                            for f_name in zipped.namelist():
                                if f_name.endswith(".tsv"):
                                    raw_data = pd.read_csv(zipped.open(f_name), sep="\t").replace({float('nan'):None})
                                    raw_data = self._secondaryParse(raw_data)
                                    dataset = DatasetFileModel(
                                        columns=list(raw_data.columns),
                                        rows=list(raw_data.apply(lambda series : series.to_dict(), axis=1))
                                    )
                                    ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=dataclasses.asdict(dataset))
                    else:
                        ret_val.RequestErrored(msg=missing_file_msg, status=ResponseStatus.BAD_REQUEST)
                else:
                    ret_val.RequestErrored(msg=f"Could not find a dataset for {safe_game_id} in {safe_month:>02}/{safe_year:>04}", status=ResponseStatus.NOT_FOUND)
            except url_error.HTTPError as err:
                current_app.logger.error(f"HTTP error getting {file_type} file from {file_link}:\n{err}")
                ret_val.ServerErrored(msg=f"Server experienced an error retrieving {file_type} file from {safe_game_id} in {safe_month:>02}/{safe_year:>04}.", status=ResponseStatus.INTERNAL_ERR)
            except Exception as err: # pylint: disable=broad-exception-caught
                msg = f"Unexpected error while retrieving dataset file contents from {safe_game_id} in {safe_month:>02}/{safe_year:>04}!"
                current_app.logger.error(f"{msg}\n{type(err)}:\n{err}")
                ret_val.ServerErrored(msg=msg, status=ResponseStatus.INTERNAL_ERR)
        elif safe_game_id is None:
            ret_val.RequestErrored(msg=f"Invalid GameID '{game_id}'", status=ResponseStatus.BAD_REQUEST)
        elif safe_year is None:
            ret_val.RequestErrored(msg=f"Invalid Year '{year}'", status=ResponseStatus.BAD_REQUEST)
        elif safe_month is None:
            ret_val.RequestErrored(msg=f"Invalid Month '{month}'", status=ResponseStatus.BAD_REQUEST)
        elif safe_filetype is None:
            ret_val.RequestErrored(msg=f"Invalid File Type '{file_type}'", status=ResponseStatus.BAD_REQUEST)

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
