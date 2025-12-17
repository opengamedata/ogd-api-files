"""
ServerConfigSchema

Contains a Schema class for managing config data for server configurations.
"""

# import standard libraries
from typing import Any, Dict, Final, Optional, Self

# import 3rd-party libraries

# import OGD libraries
from ogd.apis.configs.ServerConfig import ServerConfig
from ogd.common.utils.typing import Map

# import local files

class FileAPIConfig(ServerConfig):
    _DEFAULT_FILE_LIST_URL : Final[str] = 'https://opengamedata.fielddaylab.wisc.edu/data/file_list.json'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(FileAPIConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self, name:str, all_elements:Dict[str, Any]):
        if not hasattr(self, '_initialized'):
            self._game_mapping  : Dict[str, Dict[str, str]] = all_elements.get("BIGQUERY_GAME_MAPPING", {})
            self._file_list_url : str                       = all_elements.get("FILE_LIST_URL", FileAPIConfig._DEFAULT_FILE_LIST_URL)

            _used = {"DB_CONFIG", "OGD_CORE_PATH", "GOOGLE_CLIENT_ID"}
            _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
            super().__init__(
                name=name,
                debug_level=None,
                version=None,
                other_elements=_leftovers
            )
            self._initialized = True

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

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None) -> "FileAPIConfig":
        return FileAPIConfig(name=name, all_elements=unparsed_elements)
