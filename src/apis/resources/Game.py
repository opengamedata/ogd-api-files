# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import local files
from apis.configs.FileAPIConfig import FileAPIConfig
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

        ret_val.ServerErrored("This endpoint is not yet implemented!")

        return ret_val.AsFlaskResponse
