# import libraries
import requests
from typing import Optional
from unittest import TestCase, TestSuite, main
# import locals
from tests.schemas.TestConfigSchema import TestConfigSchema
from tests.utils.SendRequest import SendTestRequest
from tests.config.t_config import settings

_config = TestConfigSchema.FromDict(name="HelloAPITestConfig", all_elements=settings, logger=None)

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
    def setUp(self):
        self.url    : str                         = f"{_config.ExternEndpoint}/"
        self.result : Optional[requests.Response] = SendTestRequest(url=self.url, request="GET", params={}, config=_config)

    def tearDown(self):
        if self.result is not None:
            self.result.close()

    def test_Responded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["success"], True)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["data"], {"message":"hello, world"})
        else:
            self.fail(f"No result from request to {self.url}")

class t_Version(TestCase):
    def setUp(self):
        self.url    : str                         = f"{_config.ExternEndpoint}/version"
        self.result : Optional[requests.Response] = SendTestRequest(url=self.url, request="GET", params={}, config=_config)

    def tearDown(self):
        if self.result is not None:
            self.result.close()

    def test_Responded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["success"], True)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["data"], {"message":_config.APIVersion})
        else:
            self.fail(f"No result from request to {self.url}")

if __name__ == "__main__":
    main()