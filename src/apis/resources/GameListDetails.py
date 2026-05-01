from typing import Dict

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.apis.models.files.GameSummary import GameSummary as GameSummaryModel
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import local files
from apis.resources.GameSummary import GameSummary
from configs.FileAPIConfig import FileAPIConfig
from utils.utils import GetFileList

class GameListDetails(Resource):
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

        summaries : Dict[str, GameSummaryModel] = {}

        try:
            cfg       : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
            file_list : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
            for game_id,datasets in file_list.Games.items():
                datadates = set(str(dataset.StartDate).replace("/", "-") for dataset in datasets.Datasets.values())
                session_avg = GameSummary._averageSessions(
                    monthly_session_counts=[datasets.Datasets[key].SessionCount for key in sorted(datasets.Datasets.keys(), reverse=True)]
                )

                summaries[game_id] = GameSummaryModel(
                    game_id=game_id,
                    dataset_count=len(datadates),
                    session_avg=session_avg,
                    initial_dataset=min(datadates)
                )

            # If the given game isn't in our dictionary, or our dictionary doesn't have any date ranges for this game
            if file_list.Games is None or len(file_list.Games) < 1:
                ret_val.RequestErrored(msg="Could not find any games!", status=ResponseStatus.NOT_FOUND)
            else:
                ret_val.RequestSucceeded(
                    msg="Retrieved list of games with available datasets",
                    val={ key : val.AsDict for key,val in summaries.items() }
                )
        except Exception as err:
            msg = "Unexpected error while retrieving list of games with available datasets!"
            current_app.logger.error(f"{msg}\n{type(err)}:\n{err}")
            ret_val.ServerErrored(msg=msg)

        return ret_val.AsFlaskResponse
