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
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

_testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
_level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
Logger.std_logger.setLevel(_level)

class test_GameDatasets(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url    : str
        cls.result : Optional[requests.Response]
        cls.content : Optional[APIResponse]    = None

        cls.url    = f"{_testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/list"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.result = TestRequest(url=cls.url, request="GET", timeout=2, logger=Logger.std_logger)
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
            self.fail(f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertEqual(self.content.Status, ResponseStatus.SUCCESS)
        else:
            self.fail(f"No JSON content from request to {self.url}")

    def test_Correct(self):
        _expected_data = {
            'year': 2021,
            'month': 5,
            'total_sessions': 808
        }
        if self.content is not None:
            self.assertIsInstance(self.content.Value, dict)
            # check game ID
            self.assertIn("game_id", self.content.Value.keys(), "Response did not contain game_id")
            self.assertEqual(self.content.Value.get("game_id", "NOT FOUND"), "AQUALAB")
            # check sessions element
            self.assertIn("datasets", self.content.Value.keys(), "Response did not contain datasets")
            datasets = self.content.Value.get('datasets', [])
            self.assertIsInstance(datasets, list)
            self.assertGreaterEqual(len(datasets), 2) # Aqualab should definitely have more than 2 months
            self.assertEqual(datasets[1], _expected_data)
        else:
            self.fail(f"No JSON content from request to {self.url}")

class test_GameDatasetInfo(TestCase):
    def setUp(self):
        self.url    : str
        self.result : Optional[requests.Response]
        self.content : Optional[APIResponse]    = None

        self.url    = f"{_testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/01/2024/files/"
        Logger.Log(f"Sending request to {self.url}", logging.INFO)
        self.result = TestRequest(url=self.url, request="GET", timeout=3, logger=Logger.std_logger)
        if self.result is not None:
            try:
                _raw = self.result.json()
            except JSONDecodeError as err:
                print(f"Could not parse {self.result.text} to JSON!\n{err}")
            else:
                self.content = APIResponse.FromDict(all_elements=_raw)

    @staticmethod
    def RunAll():
        pass

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
        expected_data = {
            "detectors_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/src/ogd/games/AQUALAB/detectors",
            "events_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json",
            "events_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_all-events.zip",
            "events_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "features_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/src/ogd/games/AQUALAB/features",
            "first_month":1,
            "first_year":2024,
            "found_matching_range":True,
            "last_month":1,
            "last_year":2024,
            "players_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fsession-template%2Fdevcontainer.json",
            "players_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_player-features.zip",
            "players_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "population_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_population-features.zip",
            "population_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "raw_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_events.zip",
            "sessions_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fplayer-template%2Fdevcontainer.json",
            "sessions_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_session-features.zip",
            "sessions_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
        }
        # HACK: Currently, there's some mismatches in naming conventions between old and new, as well as in how we're parsing out what's what.
        # So, temporarily changing the "expected" from what would be truly ideal behavior, to what is expected given the shortcomings of the packages we're depending on.
        # This allows us to watch for regressions due to changes in the FileAPI code, and can be reverted when we get upstream improvements to the packages/what's actually named what on the server
        expected_data['raw_file'] = expected_data['events_file']
        expected_data['events_file'] = None

        if self.content is not None:
            self.assertEqual(self.content.Value.keys(), expected_data.keys(), msg="Mismatching keys between response and expected")
            for key, val in expected_data.items():
                self.assertEqual(self.content.Value.get(key), val, msg=f"Mismatch for key {key}")
        else:
            self.fail(f"No JSON content from request to {self.url}")

if __name__ == "__main__":
    unittest.main()
