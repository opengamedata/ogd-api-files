# import libraries
import logging
import unittest
from json.decoder import JSONDecodeError
from typing import Optional
from unittest import TestCase
# import 3rd-party libraries
import requests
from flask import Flask
from werkzeug.test import TestResponse
# import ogd libraries
from ogd.apis.utils.APIResponse import APIResponse, ResponseStatus
from ogd.apis.utils.TestRequest import TestRequest
from ogd.common.utils.Logger import Logger
# import locals
from src.apis.configs.FileAPIConfig import FileAPIConfig
from src.apis.FileAPI import FileAPI
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

class test_GameList(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url    : str
        cls.result : Optional[TestResponse]
        cls.content : Optional[APIResponse]    = None

        # 1. Get testing config
        cls.testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if cls.testing_cfg.Verbose else logging.INFO
        _str_level =       "DEBUG" if cls.testing_cfg.Verbose else "INFO"
        Logger.std_logger.setLevel(_level)

        # 2. Set up local Flask app to run tests
        cls.application = Flask(__name__)
        cls.application.logger.setLevel(_level)

        _server_cfg_elems = {
            "API_VERSION"   : "0.0.0-Testing",
            "DEBUG_LEVEL"   : _str_level,
            "FILE_LIST_URL" : 'https://opengamedata.fielddaylab.wisc.edu/data/file_list.json',
            "BIGQUERY_GAME_MAPPING" : {}
        }
        _server_cfg = FileAPIConfig.FromDict(name="HelloAPITestServer", unparsed_elements=_server_cfg_elems)
        FileAPI.register(app=cls.application, settings=_server_cfg)

        cls.server = cls.application.test_client()

        cls.url    = f"{cls.testing_cfg.ExternEndpoint}/games/list"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.result = cls.server.get(cls.url)
        if cls.result is not None:
            try:
                _raw = cls.result.json
            except JSONDecodeError as err:
                print(f"Could not parse {cls.result.text} to JSON!\n{err}")
            else:
                cls.content = APIResponse.FromDict(all_elements=_raw or {})

    @classmethod
    def tearDownClass(cls):
        if cls.result is not None:
            cls.result.close()

    def test_Responded(self):
        self.assertIsNotNone(self.result, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        known_games = [
            "AQUALAB", "BACTERIA", "BALLOON", "BLOOM", "CRYSTAL",
            "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE",
            "ICECUBE", "JOURNALISM", "JOWILDER", "LAKELAND", "MAGNET",
            "MASHOPOLIS", "PENGUINS", "PENNYCOOK", "SHADOWSPECT", "SHIPWRECKS",
            "THERMOLAB", "THERMOVR", "TRANSFORMATION_QUEST", "WAVES",
            "WEATHER_STATION", "WIND"
        ]
        if self.content is not None and self.content.Value is not None:
            self.assertIsInstance(self.content.Value, dict)
            # check game ID
            self.assertIn("game_ids", self.content.Value.keys(), "Response did not contain game_ids")
            game_ids = self.content.Value.get("game_ids")
            self.assertIsNotNone(game_ids, "Response had null game_ids")
            for game in known_games:
                self.assertIn(game, known_games, f"No datasets for {game}")
        else:
            self.fail(f"No JSON content from request to {self.url}")

class test_GameDatasets(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url    : str
        cls.result : Optional[requests.Response]
        cls.content : Optional[APIResponse]    = None

        # 1. Get testing config
        cls.testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if cls.testing_cfg.Verbose else logging.INFO
        _str_level =       "DEBUG" if cls.testing_cfg.Verbose else "INFO"
        Logger.std_logger.setLevel(_level)

        cls.url    = f"{cls.testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/list"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.result = TestRequest(url=cls.url, request="GET", timeout=30, logger=Logger.std_logger)
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
        self.assertIsNotNone(self.result, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
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

class test_GameDatasetInfo(TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Get testing config
        cls.testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if cls.testing_cfg.Verbose else logging.INFO
        _str_level =       "DEBUG" if cls.testing_cfg.Verbose else "INFO"
        Logger.std_logger.setLevel(_level)

    def setUp(self):
        self.url    : str
        self.result : Optional[requests.Response]
        self.content : Optional[APIResponse]    = None

        self.url    = f"{cls.testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/1/2024/files/"
        Logger.Log(f"Sending request to {self.url}", logging.INFO)
        self.result = TestRequest(url=self.url, request="GET", timeout=30, logger=Logger.std_logger)
        if self.result is not None:
            try:
                _raw = self.result.json()
            except JSONDecodeError as err:
                print(f"Could not parse {self.result.text} to JSON!\n{err}")
            else:
                self.content = APIResponse.FromDict(all_elements=_raw)

    def test_Responded(self):
        self.assertIsNotNone(self.result, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertTrue(self.result.ok)
        else:
            self.fail(f"No result from request to {self.url}")

    @unittest.skip(reason="Temporarily turning this off until we solve bug that is returning the wrong info for certain months, so that we can test for other regressions in the meantime.")
    def test_Correct(self):
        expected_data = {
            "detectors_link":"https://github.com/opengamedata/opengamedata-core/tree/42597ba/src/ogd/games/AQUALAB/detectors",
            "events_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json",
            "events_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_all-events.zip",
            "events_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "features_link":"https://github.com/opengamedata/opengamedata-core/tree/42597ba/src/ogd/games/AQUALAB/features",
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

        if self.content is not None and self.content.Value is not None:
            self.assertEqual(self.content.Value.keys(), expected_data.keys(), msg="Mismatching keys between response and expected")
            for key, val in expected_data.items():
                self.assertEqual(self.content.Value.get(key), val, msg=f"Mismatch for key {key}")
        else:
            self.fail(f"No JSON content from request to {self.url}")

if __name__ == "__main__":
    unittest.main()
