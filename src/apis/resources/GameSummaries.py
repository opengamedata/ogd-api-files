# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.enums.ResponseStatus import ResponseStatus
from ogd.apis.models.files.GameSummary import GameSummary as GameSummaryModel
from ogd.apis.models.files.GameSummaries import GameSummaries as GameSummariesModel
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import local files
from configs.FileAPIConfig import FileAPIConfig
from utils.utils import GetFileList

class GameSummaries(Resource):
    """
    Get a summary for each game with data available, including per-month number of sessions over past 12 months.

    Inputs:
    - None
    Uses:
    - Index file list
    Outputs:
    - Summary information for each game with data available.
    """
    def get(self):
        ret_val = APIResponse.Default(req_type=RESTType.GET)

        try:
            cfg       : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
            file_list : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)

            # If the file_list didn't actually have games
            if file_list.Games is not None and len(file_list.Games) > 0:
                summaries = GameSummariesModel({
                    game_id:GameSummaryModel.FromDatasetCollection(game_id=game_id, dataset_collection=datasets)
                    for game_id,datasets in file_list.Games.items()
                })
                ret_val.RequestSucceeded(msg="Retrieved list of game summaries", val=summaries.AsDict)
            else:
                ret_val.RequestErrored(msg="Could not find any games!", status=ResponseStatus.NOT_FOUND)
        except Exception as err: # pylint: disable=broad-exception-caught
            msg = "Unexpected error while retrieving list of game summaries!"
            current_app.logger.error(f"{msg}\n{type(err)}:\n{err}")
            ret_val.ServerErrored(msg=msg)

        return ret_val.AsFlaskResponse
