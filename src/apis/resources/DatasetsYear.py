# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import local files
from apis.configs.FileAPIConfig import FileAPIConfig
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

        ret_val.ServerErrored("This endpoint is not yet implemented!")

        return ret_val.AsFlaskResponse
