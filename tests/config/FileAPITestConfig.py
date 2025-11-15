"""
ServerConfigSchema

Contains a Schema class for managing config data for server configurations.
"""

# import standard libraries
import logging
from typing import Dict, Final, Optional, Self
from types import SimpleNamespace

# import 3rd-party libraries

# import OGD libraries
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.typing import Map

# import local files

class FileAPITestConfig(TestConfig):
    _DEFAULT_ENDPOINT    : Final[str] = "https://ogd-staging.fielddaylab.wisc.edu/wsgi-bin/opengamedata/apis/opengamedata-api-files/main/app.wsgi"
    _DEFAULT_API_VERSION : Final[str] = "Testing"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 extern_endpoint:Optional[str]=None, api_version:Optional[str]=None,
                 verbose:Optional[bool]=None, enabled_tests:Optional[Dict[str, bool]]=None,
                 other_elements:Optional[Map]=None):

        unparsed_elements : Map = other_elements or {}

        self._extern_server : str
        self._api_version   : str

        self._extern_server = extern_endpoint if extern_endpoint is not None else self._parseExternEndpoint(unparsed_elements=unparsed_elements, schema_name=name)
        self._api_version   = api_version     if api_version     is not None else self._parseAPIVersion(unparsed_elements=unparsed_elements, schema_name=name)

        super().__init__(name=name, verbose=verbose, enabled_tests=enabled_tests, other_elements=unparsed_elements)

    @property
    def ExternEndpoint(self) -> str:
        return self._extern_server

    @property
    def APIVersion(self) -> str:
        return self._api_version

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = self.Name
        return ret_val

    @classmethod
    def Default(cls):
        return FileAPITestConfig(
            name="DefaultFileAPITests",
            extern_endpoint=FileAPITestConfig._DEFAULT_ENDPOINT,
            api_version=FileAPITestConfig._DEFAULT_API_VERSION,
            verbose=FileAPITestConfig._DEFAULT_VERBOSE,
            enabled_tests=FileAPITestConfig._DEFAULT_ENABLED_TESTS,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map,
                  key_overrides:Optional[Dict[str, str]]=None,
                  default_override:Optional[Self]=None):
        return FileAPITestConfig(name=name, extern_endpoint=None, api_version=None,
                                 verbose=None, enabled_tests=None, other_elements=unparsed_elements)

    @staticmethod
    def _parseExternEndpoint(unparsed_elements:Map, schema_name:Optional[str]=None) -> str:
        ret_val : str

        ret_val = FileAPITestConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["EXTERN_ENDPOINT"],
            to_type=str,
            default_value=FileAPITestConfig._DEFAULT_ENDPOINT,
            remove_target=True,
            schema_name=schema_name
        )

        return ret_val

    @staticmethod
    def _parseAPIVersion(unparsed_elements:Map, schema_name:Optional[str]=None) -> str:
        ret_val : str

        ret_val = FileAPITestConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["API_VERSION"],
            to_type=str,
            default_value=FileAPITestConfig._DEFAULT_API_VERSION,
            remove_target=True,
            schema_name=schema_name
        )

        return ret_val
