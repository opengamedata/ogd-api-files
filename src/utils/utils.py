# import standard libraries
import json
from typing import Any, Dict, Optional
from urllib import error as url_error
from urllib import request as url_request

# import ogd libraries
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

# import 3rd-party libraries
from flask import current_app

# import local files
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from models.SanitizedParams import SanitizedParams

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

def MatchDatasetRequest(sanitary_request:SanitizedParams, available_datasets:DatasetCollectionSchema) -> Optional[DatasetSchema]:
    _matched_dataset : Optional[DatasetSchema] = None

    # Find the best match of a dataset to the requested month-year.
    # If there was no requested month-year, we skip this step.
    for _key, _dataset_schema in available_datasets.Datasets.items():
        if _dataset_schema.Key.DateFrom and _dataset_schema.Key.DateTo:
            # If this range contains the given year & month
            if (sanitary_request.Year >= _dataset_schema.Key.DateFrom.year \
            and sanitary_request.Month >= _dataset_schema.Key.DateFrom.month \
            and sanitary_request.Year <= _dataset_schema.Key.DateTo.year \
            and sanitary_request.Month <= _dataset_schema.Key.DateTo.month):
                if _dataset_schema.IsNewerThan(_matched_dataset):
                    _matched_dataset = _dataset_schema
        else:
            current_app.logger.debug(f"While searching for dataset request match, found invalid dataset key '{_dataset_schema.Key}' in the server file list.")

    return _matched_dataset
