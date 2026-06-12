# import standard libraries
import json
from typing import Any, Dict, Optional
from urllib import request as url_request

# import ogd libraries
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import 3rd-party libraries
from flask import current_app

# import local files
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

def GetFileList(url:str) -> DatasetRepositoryConfig:
    # Pull the file list data into a dictionary
    file_list_response                             = url_request.urlopen(url)
    file_list_json     : Dict[str, Dict[str, Any]] = json.loads(file_list_response.read())
    # HACK to make sure we've got a remote_url, working around bug in RepositoryIndexingConfig FromDict(...) implementation.
    if "CONFIG" in file_list_json.keys() and isinstance(file_list_json["CONFIG"], dict):
        if not "remote_url" in file_list_json["CONFIG"].keys():
            file_list_json["CONFIG"]["remote_url"] = file_list_json["CONFIG"].get("files_base", "https://opengamedata.fielddaylab.wisc.edu/")
        if not "templates_url" in file_list_json["CONFIG"].keys():
            file_list_json["CONFIG"]["templates_url"] = file_list_json["CONFIG"].get("templates_base", "https://github.com/opengamedata/opengamedata-templates")
    file_list          : DatasetRepositoryConfig   = DatasetRepositoryConfig.FromDict(name="file_list", unparsed_elements=file_list_json)
    return file_list

def FindDataset(game_id:str, year:int, month:int, available_datasets:Dict[str, DatasetCollectionSchema]) -> Optional[DatasetSchema]:
    _matched_dataset : Optional[DatasetSchema] = None

    game_datasets : DatasetCollectionSchema = available_datasets.get(game_id, DatasetCollectionSchema.Default())
    # Find the best match of a dataset to the requested month-year.
    # If there was no requested month-year, we skip this step.
    if len(game_datasets.Datasets) > 0:
        for _key, _dataset_schema in game_datasets.Datasets.items():
            if _dataset_schema.Key.DateFrom and _dataset_schema.Key.DateTo:
                # If this range contains the given year & month
                if (year >= _dataset_schema.Key.DateFrom.year \
                and month >= _dataset_schema.Key.DateFrom.month \
                and year <= _dataset_schema.Key.DateTo.year \
                and month <= _dataset_schema.Key.DateTo.month):
                    if _dataset_schema.IsNewerThan(_matched_dataset):
                        _matched_dataset = _dataset_schema
            else:
                current_app.logger.debug(f"While searching for dataset request match, found invalid dataset key '{_dataset_schema.Key}' in the server file list.")
    else:
        current_app.logger.warning(msg=f"GameID '{game_id}' has no available datasets")

    return _matched_dataset
