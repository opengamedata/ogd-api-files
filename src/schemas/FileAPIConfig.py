"""
ServerConfigSchema

Contains a Schema class for managing config data for server configurations.
"""

# import standard libraries
import logging
from typing import Any, Dict, Final

# import 3rd-party libraries

# import OGD libraries
from ogd.common.utils.SemanticVersion import SemanticVersion
from ogd.apis.schemas.ServerConfigSchema import ServerConfigSchema

# import local files

class FileAPIConfig(ServerConfigSchema):
    _DEFAULT_FILE_LIST_URL : Final[str] = 'https://opengamedata.fielddaylab.wisc.edu/data/file_list.json'


    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._game_mapping  : Dict[str, Dict[str, str]] = all_elements.get("BIGQUERY_GAME_MAPPING", {})
        self._file_list_url : str                       = all_elements.get("FILE_LIST_URL", FileAPIConfig._DEFAULT_FILE_LIST_URL)

        _used = {"DB_CONFIG", "OGD_CORE_PATH", "GOOGLE_CLIENT_ID"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        version_str = all_elements.get("API_VERSION", str(SemanticVersion(0,0,0,"version-not-set")))
        super().__init__(
            name=name,
            debug_level=all_elements.get("DEBUG_LEVEL", logging.INFO),
            version=SemanticVersion.FromString(version_str),
            other_elements=_leftovers
        )

    @property
    def GameMapping(self) -> Dict[str, Dict[str, str]]:
        return self._game_mapping

    @property
    def FileListURL(self) -> str:
        return self._file_list_url

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}"
        return ret_val

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any]) -> "FileAPIConfig":
        return FileAPIConfig(name=name, all_elements=all_elements)
