# import libraries
import requests
import unittest
from typing import Optional
from unittest import TestCase, TestSuite, main
# import locals
from tests.schemas.TestConfigSchema import TestConfigSchema
from tests.utils.SendRequest import SendTestRequest
from tests.config.t_config import settings

_config = TestConfigSchema.FromDict(name="FileAPITestConfig", all_elements=settings, logger=None)

class t_FileAPI:
    @staticmethod
    def RunAll():
        pass

@unittest.skip("This endpoint is not in use; needs access to database")
class t_GameUsageByMonth(TestCase):
    def setUp(self):
        self.url    : str
        self.result : Optional[requests.Response]

        params = {
            "game_id" : "AQUALAB",
            "year"    : 2024,
            "month"   : 1
        }
        self.url    = f"{_config.ExternEndpoint}/getGameUsageByMonth"
        self.result = SendTestRequest(url=self.url, request="GET", params=params, config=_config)

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

    # def test_Correct(self):
    #     if self.result is not None:
    #         self.assertEqual(self.result.json()["data"], {"message":"hello, world"})
    #     else:
    #         self.fail(f"No result from request to {self.url}")

class t_MonthlyGameUsage(TestCase):
    def setUp(self):
        self.url    : str
        self.result : Optional[requests.Response]

        params = {
            "game_id" : "AQUALAB"
        }
        self.url    = f"{_config.ExternEndpoint}/getMonthlyGameUsage"
        self.result = SendTestRequest(url=self.url, request="GET", params=params, config=_config)

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

    # def test_Correct(self):
    #     if self.result is not None:
    #         self.assertEqual(self.result.json()["data"], {"message":_config.APIVersion})
    #     else:
    #         self.fail(f"No result from request to {self.url}")

class t_GameFileInfoByMonth(TestCase):
    def setUp(self):
        self.url    : str
        self.result : Optional[requests.Response]

        params = {
            "game_id" : "AQUALAB",
            "year"    : 2024,
            "month"   : 1
        }
        self.url    = f"{_config.ExternEndpoint}/getGameFileInfoByMonth"
        self.result = SendTestRequest(url=self.url, request="GET", params=params, config=_config)

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

    # def test_Correct(self):
    #     if self.result is not None:
    #         self.assertEqual(self.result.json()["data"], {"message":_config.APIVersion})
    #     else:
    #         self.fail(f"No result from request to {self.url}")

if __name__ == "__main__":
    main()
