from typing import Optional

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

        # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
        if not parsed_game_id in file_list.Games or len(file_list.Games[parsed_game_id].Datasets) == 0:
            ret_val.ServerErrored(msg=f"GameID '{parsed_game_id}' not found in list of games with datasets, or had no datasets listed")
            return ret_val.AsFlaskResponse

        dataset_list = DatasetListModel(datasets={
            Dataset.FromDatasetSchema(dataset)
            for dataset in game_datasets.Datasets.values()
        })

        sessions = []

        # rangeKey format is GAMEID_YYYYMMDD_to_YYYYMMDD or GAME_ID_YYYYMMDD_to_YYYYYMMDD
        for _dataset in game_datasets.Datasets.values():

            # If this rangeKey matches the expected format
            if _dataset.Key.DateFrom and _dataset.Key.DateTo and year in {_dataset.Key.DateFrom.year, _dataset.Key.DateTo.year, None}: # len(rangeKeyParts) == 4:
                # Capture the number of sessions for this YYYYMM
                sessions.append(
                    DatasetModel(
                        year            = _dataset.Key.DateFrom.year,
                        month           = _dataset.Key.DateFrom.month,
                        total_sessions  = _dataset.SessionCount or 0,
                        sessions_file   = f"{file_list.RemoteURL}{_dataset.SessionsFile}"   if _dataset.SessionsFile   is not None else "SESSIONS FILE NOT FOUND",
                        players_file    = f"{file_list.RemoteURL}{_dataset.PlayersFile}"    if _dataset.PlayersFile    is not None else "PLAYERS FILE NOT FOUND",
                        population_file = f"{file_list.RemoteURL}{_dataset.PopulationFile}" if _dataset.PopulationFile is not None else "POPULATION FILE NOT FOUND"
                    ).AsDict
                )


        responseData = { "game_id": parsed_game_id, "datasets": sessions }
        ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=responseData)

        return ret_val.AsFlaskResponse