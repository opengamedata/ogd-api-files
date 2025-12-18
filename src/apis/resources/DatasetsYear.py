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

class DatasetsYear(Resource):
    """
    Get a list of datasets within a single year for a game

    Inputs:
    - Game ID, Year
    Outputs:
    - Not implemented
    """
    def get(self, game_id, year):
        ret_val = APIResponse.Default(req_type=RESTType.GET)
        
        game_id = SanitizedParams.sanitizeGameId(game_id)
        if game_id is None or game_id == "":
            ret_val.RequestErrored(msg=f"Bad GameID parameter '{game_id}'")
            return ret_val.AsFlaskResponse

        year = SanitizedParams.sanitizeYear(year)
        if year is None:
            ret_val.RequestErrored(msg=f"Bad Year parameter '{year}'")
            return ret_val.AsFlaskResponse

        cfg           : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
        file_list     : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
        game_datasets : DatasetCollectionSchema = file_list.Games.get(game_id, DatasetCollectionSchema.Default())

        # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
        if not game_id in file_list.Games or len(file_list.Games[game_id].Datasets) == 0:
            ret_val.ServerErrored(msg=f"GameID '{game_id}' not found in list of games with datasets, or had no datasets listed")
            return ret_val.AsFlaskResponse

        sessions = []

        # rangeKey format is GAMEID_YYYYMMDD_to_YYYYMMDD or GAME_ID_YYYYMMDD_to_YYYYYMMDD
        for _dataset in game_datasets.Datasets.values():

            # If this rangeKey matches the expected format
            if _dataset.Key.DateFrom and _dataset.Key.DateTo and year in {_dataset.Key.DateFrom.year, _dataset.Key.DateTo.year}:
                # Capture the number of sessions for this YYYYMM
                sessions.append({
                    "year"            : _dataset.Key.DateFrom.year,
                    "month"           : _dataset.Key.DateFrom.month,
                    "total_sessions"  : _dataset.SessionCount,
                    "sessions_file"   : f"{file_list.RemoteURL}{_dataset.SessionsFile}"   if _dataset.SessionsFile   is not None else None,
                    "players_file"    : f"{file_list.RemoteURL}{_dataset.PlayersFile}"    if _dataset.PlayersFile    is not None else None,
                    "population_file" : f"{file_list.RemoteURL}{_dataset.PopulationFile}" if _dataset.PopulationFile is not None else None
                })


        responseData = { "game_id": game_id, "datasets": sessions }
        ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=responseData)

        return ret_val.AsFlaskResponse