import dataclasses
from typing import List, Optional

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, RESTType
from ogd.apis.models.files.DatasetList import DatasetList as DatasetListModel
from ogd.apis.models.files.DatasetList import Dataset
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from models.SanitizedParams import SanitizedParams
from utils.utils import GetFileList

class DatasetList(Resource):
    """
    Get the per-month number of sessions for a given game

    Inputs:
    - Game ID
    Uses:
    - Index file list
    Outputs:
    - Session count for each month of game's data
    """
    def get(self, game_id:str, year:Optional[int]=None):
        ret_val = APIResponse.Default(req_type=RESTType.GET)
        
        parsed_game_id = SanitizedParams.sanitizeGameId(game_id)
        if parsed_game_id is None or parsed_game_id == "":
            ret_val.RequestErrored(msg=f"Bad GameID '{parsed_game_id}'")
            return ret_val.AsFlaskResponse

        cfg           : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
        file_list     : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
        game_datasets : DatasetCollectionSchema = file_list.Games.get(parsed_game_id, DatasetCollectionSchema.Default())

        if parsed_game_id in file_list.Games and len(file_list.Games[parsed_game_id].Datasets) > 0:
            # inject file_list.RemoteURL into the file locations for the datasets. In particular, probably need to set each dataset's base file location to the RemoteURL base.
            if file_list.RemoteURL is not None:
                for dataset in game_datasets.Datasets.values():
                    dataset._base_files_location = file_list.RemoteURL
            as_list = [
                    Dataset.FromDatasetSchema(dataset)
                    for dataset in game_datasets.Datasets.values()
                    if dataset.Key.DateFrom and dataset.Key.DateTo and year in {dataset.Key.DateFrom.year, dataset.Key.DateTo.year, None}
            ]
            dataset_list_model = DatasetListModel(game_id=parsed_game_id, datasets=as_list)

            value = { "game_id": parsed_game_id, "datasets": dataclasses.asdict(dataset_list_model) }
            ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=value)
        # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
        else:
            ret_val.ServerErrored(msg=f"GameID '{parsed_game_id}' not found in list of games with datasets, or had no datasets listed")

        return ret_val.AsFlaskResponse