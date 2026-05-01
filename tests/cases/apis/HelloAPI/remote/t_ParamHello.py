# import libraries
import logging
import unittest
from typing import Optional
from unittest import TestCase
# import ogd libraries
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse, ResponseStatus
from ogd.common.utils.Logger import Logger
# import locals
from src.tests.config import t_config
from tests.FileAPITestConfig import FileAPITestConfig

_testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=t_config.settings)
_level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO

@unittest.skip("Haven't yet implemented the parameterized calls to HelloAPI")
class test_ParamHello(TestCase):
    @classmethod
    def setUpClass(cls):
        Logger.std_logger.setLevel(_level)

        cls.url     : str                         = f"{_testing_cfg.ExternEndpoint}/hello"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.content : Optional[APIResponse]    = APIRequest(url=cls.url, request_type="GET", params={}, timeout=30).Execute(logger=Logger.std_logger)

    def test_Responded(self):
        self.assertIsNotNone(self.content, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertEqual(self.content.Status, ResponseStatus.OK)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        if self.content is not None:
            self.assertEqual(self.content.Message, "Hello! You GETted successfully!")
        else:
            self.fail(f"No JSON content from request to {self.url}")

if __name__ == "__main__":
    unittest.main()