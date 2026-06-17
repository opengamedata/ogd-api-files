# import standard libraries
from typing import Optional

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.enums.ResponseStatus import ResponseStatus
from ogd.apis.models.files.DatasetManifest import DatasetManifest as DatasetManifestModel
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from utils.SanitizedParams import SanitizedParams
from utils.utils import GetFileList, FindDataset

class DatasetManifest(Resource):
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

        safe_game_id = SanitizedParams.SanitizeGameID(game_id=game_id)
        safe_year    = SanitizedParams.SanitizeYear(year=year)
        safe_month   = SanitizedParams.SanitizeMonth(month=month)
        if safe_game_id and safe_year and safe_month:
            try:
                cfg             : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
                file_list       : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
                matched_dataset : Optional[DatasetSchema] = FindDataset(game_id=safe_game_id, year=safe_year, month=safe_month, available_datasets=file_list.Games)

                if matched_dataset and matched_dataset.Key.DateFrom and matched_dataset.Key.DateTo:
                    manifest = DatasetManifestModel(dataset_schema=matched_dataset)
                    if file_list.RemoteURL is not None:
                        manifest.BaseFileLocation = file_list.RemoteURL

                    ret_val.RequestSucceeded(msg=f"Retrieved dataset manifest for {safe_game_id} in {safe_month:>02}/{safe_year:>04}", val=manifest.AsDict)
                else:
                    ret_val.RequestErrored(msg=f"Could not find a dataset for {safe_game_id} in {safe_month:>02}/{safe_year:>04}", status=ResponseStatus.NOT_FOUND)
            except Exception as err: # pylint: disable=broad-exception-caught
                msg = f"Unexpected error while retrieving dataset resources for {safe_game_id} in {safe_month:>02}/{safe_year:>04}!"
                current_app.logger.error(f"{msg}\n{type(err)}:\n{err}")
                ret_val.ServerErrored(msg=msg)
        elif safe_game_id is None:
            ret_val.RequestErrored(msg=f"Invalid GameID '{game_id}'", status=ResponseStatus.BAD_REQUEST)
        elif safe_year is None:
            ret_val.RequestErrored(msg=f"Invalid Year '{year}'", status=ResponseStatus.BAD_REQUEST)
        elif safe_month is None:
            ret_val.RequestErrored(msg=f"Invalid Month '{month}'", status=ResponseStatus.BAD_REQUEST)

        return ret_val.AsFlaskResponse
