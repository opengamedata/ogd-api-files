# import libraries
import logging
import unittest
from json.decoder import JSONDecodeError
from typing import Optional
from unittest import TestCase
# import 3rd-party libraries
import requests
# import ogd libraries
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse, ResponseStatus
from ogd.common.utils.Logger import Logger
# import locals
from tests.config import t_config
from tests.FileAPITestConfig import FileAPITestConfig

_testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=t_config.settings)
_level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO

class test_Version(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url    : str                         = f"{_testing_cfg.ExternEndpoint}/version"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.content : Optional[APIResponse] = APIRequest(url=cls.url, request_type="GET", params={}, timeout=30).Execute(logger=Logger.std_logger)

    def test_Responded(self):
        self.assertIsNotNone(self.content, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertTrue(self.content.Status == ResponseStatus.OK)
        else:
            self.fail(f"No result from request to {self.url}")

    @unittest.skip(reason="Issues in parsing of versions make this unreliable, disabling until a future release of ogd-common fixes this issue.")
    def test_Correct(self):
        if self.content is not None:
            self.assertEqual(self.content.Value, {"version":_testing_cfg.APIVersion})
        else:
            self.fail(f"No JSON content from request to {self.url}")

if __name__ == "__main__":
    unittest.main()