from typing import Optional

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.apis.models.files.GameSummary import GameSummaryResponse
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams
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
        
        game_id = SanitizedParams.sanitizeGameId(game_id)
        if game_id is None or game_id == "":
            ret_val.RequestErrored(msg=f"Bad GameID '{game_id}'")
            return ret_val.AsFlaskResponse

        cfg           : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
        file_list     : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
        game_datasets : Optional[DatasetCollectionSchema] = file_list.Games.get(game_id, None)

        if game_datasets and len(game_datasets.Datasets) > 0:
            ret_val = GameSummaryResponse.FromDatasetCollection(game_id=game_id, dataset_collection=game_datasets)
        else:
            # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
            ret_val.ServerErrored(msg=f"GameID '{game_id}' not found in list of games with datasets, or had no datasets listed")

        return ret_val.AsFlaskResponse
