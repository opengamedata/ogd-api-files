from typing import List

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.apis.models.files.GameSummary import GameSummary as GameSummaryModel
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
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

        datadates = set(str(dataset.StartDate).replace("/", "-") for dataset in game_datasets.Datasets.values())
        session_avg = GameSummary._averageSessions(
            monthly_session_counts=[game_datasets.Datasets[key].SessionCount for key in sorted(game_datasets.Datasets.keys(), reverse=True)]
        )

        model = GameSummaryModel(
            game_id=game_id,
            dataset_count=len(datadates),
            session_avg=session_avg,
            initial_dataset=min(datadates)
        )
        ret_val.RequestSucceeded(msg="Retrieved monthly game usage", val=model.AsDict)

        return ret_val.AsFlaskResponse

    @staticmethod
    def _averageSessions(monthly_session_counts:List[int | None], month_range:int=12):
        ret_val = 0

        months_counted = 0
        sum_sessions   = 0

        for month in monthly_session_counts:
            # If this month has sessions
            if month is not None and month > 0:
                # Add it to our sum
                sum_sessions += month
            # If we've found a month with sessions either this iteration or a previous iteration
            if sum_sessions > 0:
                # This month counts towards our 12 whether or not it had sessions
                months_counted += 1
            # Once we have 12 months of data we can quit
            if months_counted == month_range:
                break

        # If we counted at least one month
        if months_counted > 0:
            # Return an integer average
            ret_val = (int)(sum_sessions / months_counted)

        return ret_val