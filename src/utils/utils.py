# import standard libraries
import json
from typing import Any, Dict
from urllib import error as url_error
from urllib import request as url_request

# import ogd libraries
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig

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