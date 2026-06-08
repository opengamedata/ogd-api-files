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
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

_testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
_level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
Logger.std_logger.setLevel(_level)

class test_GameDatasets(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url    : str
        cls.content : Optional[APIResponse]    = None

        cls.url    = f"{_testing_cfg.ExternEndpoint}/games/AQUALAB/datasets"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.content = APIRequest(url=cls.url, request_type="GET", timeout=30).Execute(logger=Logger.std_logger)

    def test_Responded(self):
        self.assertIsNotNone(self.content, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertTrue(self.content.Status == ResponseStatus.OK)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        _expected_data = {
            'year': 2022,
            'month': 8,
            'total_sessions': 357,
            "sessions_file"   : "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20220801_to_20220831_0c348a5_session-features.zip",
            "players_file"    : "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20220801_to_20220831_0c348a5_player-features.zip",
            "population_file" : "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20220801_to_20220831_0c348a5_population-features.zip"
        }
        if self.content is not None and self.content.Value is not None:
            self.assertIsInstance(self.content.Value, dict)
            # check game ID
            self.assertIn("game_id", self.content.Value.keys(), "Response did not contain game_id")
            self.assertEqual(self.content.Value.get("game_id", "NOT FOUND"), "AQUALAB")
            # check sessions element
            self.assertIn("datasets", self.content.Value.keys(), "Response did not contain datasets")
            datasets = self.content.Value.get('datasets', [])
            self.assertIsInstance(datasets, list)
            self.assertGreaterEqual(len(datasets), 17) # Aqualab should definitely have more than 17 months, as long as it's been around.
            self.assertEqual(datasets[17], _expected_data)
        else:
            self.fail(f"No JSON content from request to {self.url}")
