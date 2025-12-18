# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema

# import local files
from apis.configs.FileAPIConfig import FileAPIConfig
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
        game_datasets : DatasetCollectionSchema = file_list.Games.get(game_id, DatasetCollectionSchema.Default())

        # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
        if not game_id in file_list.Games or len(file_list.Games[game_id].Datasets) == 0:
            ret_val.ServerErrored(msg=f"GameID '{game_id}' not found in list of games with datasets, or had no datasets listed")
            return ret_val.AsFlaskResponse

        datadates = set(str(dataset.StartDate) for dataset in game_datasets.Datasets.values())
        responseData = {
            "game_id": game_id,
            "dataset_count": len(datadates),
            "initial_dataset": min(datadates)
        }
        ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=responseData)

        return ret_val.AsFlaskResponse