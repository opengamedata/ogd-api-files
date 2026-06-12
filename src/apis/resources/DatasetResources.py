# import standard libraries
from typing import Final, Optional

# import 3rd-party libraries
from flask import current_app
from flask_restful import Resource

# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.apis.models.files.DatasetResources import DatasetResources as DatasetResourcesModel
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

# import local files
from configs.FileAPIConfig import FileAPIConfig
from utils.SanitizedParams import SanitizedParams
from utils.utils import GetFileList, MatchDatasetRequest

class DatasetResources(Resource):
    """
    Get info on the files that are available for the given game in the given month & year

    Inputs:
    - Game ID
    - Year
    - Month
    Outputs:
    - DatasetSchema of most recently-exported dataset for game in month
    """
    CODESPACES_BASE_URL : Final[str] = "https://codespaces.new/opengamedata/opengamedata-samples/tree/"
    GITHUB_BASE_URL     : Final[str] = "https://github.com/opengamedata/opengamedata-core/tree/"

    def get(self, game_id, month, year):
        ret_val = APIResponse.Default(req_type=RESTType.GET)

        if sanitary_params := SanitizedParams.FromParams(game_id=game_id, year=year, month=month):
            if sanitary_params.IsValid:
                try:
                    cfg           : FileAPIConfig           = FileAPIConfig("FileAPIConfig", {})
                    file_list     : DatasetRepositoryConfig = GetFileList(cfg.FileListURL)
                    game_datasets : DatasetCollectionSchema = file_list.Games.get(sanitary_params.GameID, DatasetCollectionSchema.Default())

                    # Search for the most recently modified dataset that contains the requested month and year
                    if len(game_datasets.Datasets) > 0:
                        _matched_dataset : Optional[DatasetSchema] = MatchDatasetRequest(sanitary_request=sanitary_params, available_datasets=game_datasets)

                        if _matched_dataset and _matched_dataset.Key.DateFrom and _matched_dataset.Key.DateTo:
                            if file_list.RemoteURL is not None:
                                _matched_dataset.BaseFileLocation = file_list.RemoteURL
                            
                            dataset_resources = DatasetResourcesModel.FromBaseURLs(
                                game_id=sanitary_params.GameID,
                                dataset_schema=_matched_dataset,
                                template_url_base=file_list.TemplatesBase.Location,
                                codespace_tree_url=self.CODESPACES_BASE_URL,
                                github_tree_url=self.GITHUB_BASE_URL
                            )

                            ret_val.RequestSucceeded(msg="Retrieved game file info by month", val=dataset_resources.AsDict)
                        else:
                            ret_val.RequestErrored(msg=f"Could not find a dataset for {sanitary_params.GameID} in {sanitary_params.Month:>02}/{sanitary_params.Year:>04}", status=ResponseStatus.NOT_FOUND)
                    else:
                        ret_val.RequestErrored(msg=f"GameID '{sanitary_params.GameID}' has no available datasets", status=ResponseStatus.NOT_FOUND)
                        return ret_val.AsFlaskResponse
                except Exception as err: # pylint: disable=broad-exception-caught
                    current_app.logger.error(f"{type(err)} error processing request inputs:\n{err}")
                    ret_val.ServerErrored("Unexpected error processing request inputs.")
            elif (sanitary_params.GameID is None):
                ret_val.RequestErrored(msg=f"Invalid GameID '{game_id}'", status=ResponseStatus.BAD_REQUEST)
            elif (sanitary_params.Year is None):
                ret_val.RequestErrored(msg=f"Invalid Year '{year}'", status=ResponseStatus.BAD_REQUEST)
            elif (sanitary_params.Month is None):
                ret_val.RequestErrored(msg=f"Invalid Month '{month}'", status=ResponseStatus.BAD_REQUEST)
        else:
            raise ValueError("Could not process inputs!")

        return ret_val.AsFlaskResponse
