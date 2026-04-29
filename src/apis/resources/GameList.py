# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import local files
from ogd.apis.models.files.GameList import GameList as GameListModel
from configs.FileAPIConfig import FileAPIConfig
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

        try:
            cfg       : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
            file_list : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)

            # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
            if file_list.Games is None or len(file_list.Games) < 1:
                ret_val.RequestErrored(msg="Could not find any games!", status=ResponseStatus.NOT_FOUND)
            else:
                responseData = GameListModel(game_ids=list(file_list.Games.keys()))
                ret_val.RequestSucceeded(msg="Retrieved list of games with available datasets", val=responseData)
        except Exception as err:
            msg = "Unexpected error while retrieving list of games with available datasets!"
            current_app.logger.error(f"{msg}\n{type(err)}:\n{err}")
            ret_val.ServerErrored(msg=msg)

        return ret_val.AsFlaskResponse

    @property
    def Path(self) -> str:
        return GameListModel.PATH
