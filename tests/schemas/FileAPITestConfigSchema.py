"""
ServerConfigSchema

Contains a Schema class for managing config data for server configurations.
"""

# import standard libraries
import logging
from typing import Any, Dict, Optional
from types import SimpleNamespace

# import 3rd-party libraries

# import OGD libraries
from ogd.core.schemas.configs.TestConfigSchema import TestConfigSchema

# import local files

class FileAPITestConfigSchema(TestConfigSchema):
    @staticmethod
    def DEFAULT():
        return FileAPITestConfigSchema(
            name            = "DefaultTestConfig",
            extern_endpoint = "https://ogd-staging.fielddaylab.wisc.edu/wsgi-bin/opengamedata/apis/opengamedata-api-files/main/app.wsgi",
            api_version     = "Testing",
            verbose         = False,
            enabled_tests   = {
                "HELLO" : True
            }
        )

    def __init__(self, name:str, extern_endpoint:str, api_version:str, verbose:bool, enabled_tests:Dict[str, bool], other_elements:Dict[str, Any]={}):
        self._extern_server : str             = extern_endpoint
        self._api_version   : str             = api_version
        super().__init__(name=name, verbose=verbose, enabled_tests=enabled_tests, other_elements=other_elements)

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]):
        _extern_endpoint : str
        _verbose         : bool
        _enabled_tests   : Dict[str, bool]
        if "EXTERN_ENDPOINT" in all_elements.keys():
            _extern_endpoint = FileAPITestConfigSchema._parseExternEndpoint(all_elements["EXTERN_ENDPOINT"], logger=logger)
        else:
            _extern_endpoint = FileAPITestConfigSchema.DEFAULT().ExternEndpoint
            _msg = f"{name} config does not have an 'EXTERN_ENDPOINT' element; defaulting to extern_endpoint={_extern_endpoint}"
            if logger:
                logger.warning(_msg, logging.WARN)
            else:
                print(logger)
        if "API_VERSION" in all_elements.keys():
            _api_version = FileAPITestConfigSchema._parseAPIVersion(all_elements["API_VERSION"], logger=logger)
        else:
            _api_version = FileAPITestConfigSchema.DEFAULT().APIVersion
            _msg = f"{name} config does not have an 'API_VERSION' element; defaulting to api_version={_api_version}"
            if logger:
                logger.warning(_msg, logging.WARN)
            else:
                print(_msg)

        _used = {"EXTERN_ENDPOINT", "API_VERSION"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        # TODO : TUrns out we should have never tried to do the separation of FromDict, since this doesn't give a good way to pass up to parent class.
        # When we change this, need to come back and remove this hack.
        _parent = TestConfigSchema.FromDict(name=name, all_elements=_leftovers, logger=logger)
        _parent_used = {"VERBOSE", "ENABLED"}
        _leftovers = { key : val for key,val in _leftovers.items() if key not in _used }
        return FileAPITestConfigSchema(name=name, extern_endpoint=_extern_endpoint, api_version=_api_version, verbose=_parent.Verbose, enabled_tests=_parent.EnabledTests, other_elements=_leftovers)

    @property
    def ExternEndpoint(self) -> str:
        return self._extern_server

    @property
    def APIVersion(self) -> str:
        return self._api_version

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}"
        return ret_val

    @staticmethod
    def _parseExternEndpoint(endpoint, logger:Optional[logging.Logger]) -> str:
        ret_val : str
        if isinstance(endpoint, str):
            ret_val = endpoint
        else:
            ret_val = str(endpoint)
            _msg = f"Config external endpoint was unexpected type {type(endpoint)}, defaulting to str(endpoint) = {ret_val}."
            if logger:
                logger.warning(_msg, logging.WARN)
            else:
                print(_msg)
        return ret_val

    @staticmethod
    def _parseAPIVersion(version, logger:Optional[logging.Logger]) -> str:
        ret_val : str
        if isinstance(version, str):
            ret_val = version
        else:
            ret_val = str(version)
            _msg = f"Config API version was unexpected type {type(version)}, defaulting to str(version) = {ret_val}."
            if logger:
                logger.warning(_msg, logging.WARN)
            else:
                print(_msg)
        return ret_val
