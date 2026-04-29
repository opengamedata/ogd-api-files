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

class test_Hello(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_config = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=t_config.settings)
        _level       = logging.DEBUG if cls.test_config.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        cls.base_url     : str                         = f"{cls.test_config.ExternEndpoint}/hello"
        Logger.Log(f"Sending request to {cls.base_url}", logging.INFO)
        cls.content : Optional[APIResponse]    = APIRequest(url=cls.base_url, request_type="GET", params={}, timeout=30).Execute(logger=Logger.std_logger)

    def test_Responded(self):
        self.assertIsNotNone(self.content, f"No result from request to {self.base_url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertEqual(self.content.Status, ResponseStatus.OK)
        else:
            self.fail(f"No result from request to {self.base_url}")

    def test_Correct(self):
        if self.content is not None:
            self.assertEqual(self.content.Message, "Hello! You GETted successfully!")
        else:
            self.fail(f"No JSON content from request to {self.base_url}")
