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

    @unittest.skip("Haven't sorted out full expected data yet.")
    def test_Correct(self):
        if self.result is not None:
            self.assertEqual(self.result.json()["data"], {"message":_config.APIVersion})
        else:
            self.fail(f"No result from request to {self.url}")

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

    def test_Correct(self):
        expected_data = {
            "detectors_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/games/aqualab/detectors",
            "events_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json",
            "events_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_all-events.zip",
            "events_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "features_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/games/aqualab/features",
            "first_month":1,
            "first_year":2024,
            "found_matching_range":True,
            "last_month":1,
            "last_year":2024,
            "players_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fsession-template%2Fdevcontainer.json","players_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_player-features.zip","players_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab","population_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_population-features.zip","population_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab","raw_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_events.zip","sessions_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fplayer-template%2Fdevcontainer.json","sessions_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_session-features.zip","sessions_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab"
        }
        if self.result is not None:
            self.assertEqual(self.result.json()["data"], expected_data)
        else:
            self.fail(f"No result from request to {self.url}")

if __name__ == "__main__":
    main()
