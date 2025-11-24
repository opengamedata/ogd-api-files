# import libraries
import logging
import unittest
from json.decoder import JSONDecodeError
from typing import Optional
from unittest import TestCase
# import 3rd-party libraries
import requests
# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, ResponseStatus
from ogd.apis.utils.TestRequest import TestRequest
from ogd.common.utils.Logger import Logger
# import locals
from tests.config import t_config
from tests.FileAPITestConfig import FileAPITestConfig

class test_Hello(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_config = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=t_config.settings)
        _level       = logging.DEBUG if cls.test_config.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        cls.base_url     : str                         = f"{cls.test_config.ExternEndpoint}/hello"
        Logger.Log(f"Sending request to {cls.base_url}", logging.INFO)
        cls.result  : Optional[requests.Response] = TestRequest(url=cls.base_url, request="GET", params={}, timeout=2, logger=Logger.std_logger)
        cls.content : Optional[APIResponse]    = None
        if cls.result is not None:
            try:
                _raw = cls.result.json()
            except JSONDecodeError as err:
                print(f"Could not parse {cls.result.text} to JSON!\n{err}")
            else:
                cls.content = APIResponse.FromDict(all_elements=_raw)

    @classmethod
    def tearDownClass(cls):
        if cls.result is not None:
            cls.result.close()

    @staticmethod
    def RunAll():
        pass

    def test_Responded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.base_url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertEqual(self.content.Status, ResponseStatus.SUCCESS)
        else:
            self.fail(f"No result from request to {self.base_url}")

    def test_Correct(self):
        if self.content is not None:
            self.assertEqual(self.content.Message, "Hello! You GETted successfully!")
        else:
            self.fail(f"No JSON content from request to {self.base_url}")

if __name__ == "__main__":
    unittest.main()
