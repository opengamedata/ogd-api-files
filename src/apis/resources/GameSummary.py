import dataclasses
from typing import Optional

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.enums.ResponseStatus import ResponseStatus
from ogd.apis.models.files.GameSummary import GameSummary as GameSummaryModel
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from utils.SanitizedParams import SanitizedParams
from utils.utils import GetFileList


class GameSummary(Resource):
    """
    Get a summary of a single game

    Inputs:
    - Game ID
    Outputs:
    - Not implemented
    """
    def get(self, game_id):
        ret_val = APIResponse.Default(req_type=RESTType.GET)
        
        if safe_game_id := SanitizedParams.SanitizeGameID(game_id):
            try:
                cfg           : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
                file_list     : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
                game_datasets : Optional[DatasetCollectionSchema] = file_list.Games.get(safe_game_id, None)

                if game_datasets and len(game_datasets.Datasets) > 0:
                    summary = GameSummaryModel.FromDatasetCollection(game_id=safe_game_id, dataset_collection=game_datasets)
                    ret_val.RequestSucceeded(f"Retrieved {safe_game_id} summary", val=dataclasses.asdict(summary))
                else:
                    # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
                    ret_val.RequestErrored(msg=f"GameID '{safe_game_id}' not found in list of games with datasets, or had no datasets listed", status=ResponseStatus.NOT_FOUND)
            except Exception as err: # pylint: disable=broad-exception-caught
                msg = f"Unexpected error while retrieving {safe_game_id} summary!"
                current_app.logger.error(f"{msg}\n{type(err)}:\n{err}")
                ret_val.ServerErrored(msg=msg)
        else:
            ret_val.RequestErrored(msg=f"Invalid GameID '{game_id}'")

        return ret_val.AsFlaskResponse
