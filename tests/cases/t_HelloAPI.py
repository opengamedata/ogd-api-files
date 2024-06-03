# import libraries
import requests
from json.decoder import JSONDecodeError
from typing import Any, Dict, Optional
from unittest import TestCase, TestSuite, main
# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, RESTType, ResponseStatus
from ogd.apis.utils.SendRequest import SendTestRequest
# import locals
from tests.schemas.FileAPITestConfigSchema import FileAPITestConfigSchema
from tests.config.t_config import settings

_config = FileAPITestConfigSchema.FromDict(name="FileAPITestConfig", all_elements=settings, logger=None)

class t_HelloAPI:
    @staticmethod
    def RunAll():
        t = t_Hello()
        t.setUp()
        t.test_Responded()
        t.test_Correct()
        t = t_Version()
        t.setUp()
        t.test_Responded()
        t.test_Correct()

class t_Hello(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url     : str                         = f"{_config.ExternEndpoint}/"
        cls.result  : Optional[requests.Response] = SendTestRequest(url=cls.url, request="GET", params={}, config=_config)
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

    def test_Responded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertEqual(self.content.Status, ResponseStatus.SUCCESS)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        if self.content is not None:
            self.assertEqual(self.content.Message, "SUCCESS: hello, world")
        else:
            self.fail(f"No JSON content from request to {self.url}")

class t_Version(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url    : str                         = f"{_config.ExternEndpoint}/version"
        cls.result : Optional[requests.Response] = SendTestRequest(url=cls.url, request="GET", params={}, config=_config)
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

    def test_Responded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertEqual(self.content.Status, ResponseStatus.SUCCESS)
        else:
            self.fail(f"No JSON content from request to {self.url}")

    def test_Correct(self):
        if self.content is not None:
            self.assertEqual(self.content.Value, {"version":_config.APIVersion})
        else:
            self.fail(f"No JSON content from request to {self.url}")

if __name__ == "__main__":
    main()