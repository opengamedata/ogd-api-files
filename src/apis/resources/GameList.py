# import 3rd-party libraries
from flask import Flask, current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import local files
from apis.configs.FileAPIConfig import FileAPIConfig
from utils.utils import GetFileList

class GameList(Resource):
    """
    Get the per-month number of sessions for a given game

    Inputs:
    - Game ID
    Uses:
    - Index file list
    Outputs:
    - Session count for each month of game's data
    """
    def get(self):
        ret_val = APIResponse.Default(req_type=RESTType.GET)

        file_list     : DatasetRepositoryConfig = GetFileList(FileAPIConfig("FileAPIConfig", {}).FileListURL)

        # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
        if file_list.Games is None or len(file_list.Games) < 1:
            ret_val.ServerErrored(msg=f"Game list not found, or had no datasets listed")
            return ret_val.AsFlaskResponse

        game_ids = [game for game in file_list.Games.keys()]

        responseData = { "game_ids": game_ids }
        ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=responseData)

        return ret_val.AsFlaskResponse
