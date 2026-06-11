# import libraries
import logging
from json.decoder import JSONDecodeError
from typing import Optional
from unittest import TestCase
# import 3rd-party libraries
from flask import Flask
from werkzeug.test import TestResponse
# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, ResponseStatus
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.utils.Logger import Logger
# import locals
from src.configs.FileAPIConfig import FileAPIConfig
from src.apis.FileAPI import FileAPI
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

class LocalCase(TestCase):
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

    def test_get(self):
        _url    = f"/games/AQUALAB/datasets"
        # 1. Run request
        raw_response = self.server.get(_url)
        try:
            response = APIResponse.FromDict(all_elements=raw_response.json or {}, status=ResponseStatus(raw_response.status_code))
        except JSONDecodeError as err:
            self.fail(f"Could not parse {raw_response.text} to JSON!\n{err}")
        raw_response.close()
        # 2. Perform assertions
        if response:
            self.assertIsNotNone(response, f"No result from request to {_url}")
            self.assertTrue(response.OK, f"Bad status from {_url}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsInstance(response.Value, dict, f"Bad value type from {_url}")
            if response.Value:
                # check game ID
                self.assertIn("game_id", response.Value.keys(), "Response did not contain game_id")
                self.assertEqual(response.Value.get("game_id", "NOT FOUND"), "AQUALAB")
                # check sessions element
                self.assertIn("datasets", response.Value.keys(), "Response did not contain datasets")
                datasets = response.Value.get('datasets', [])
                self.assertIsInstance(datasets, list)
                self.assertGreaterEqual(len(datasets), 17) # Aqualab should definitely have more than 17 months, as long as it's been around.
                expected_data = {
                    'year': 2022,
                    'month': 8,
                    'total_sessions': 357,
                    "sessions_file"   : "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20220801_to_20220831_0c348a5_session-features.zip",
                    "players_file"    : "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20220801_to_20220831_0c348a5_player-features.zip",
                    "population_file" : "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20220801_to_20220831_0c348a5_population-features.zip"
                }
                self.assertEqual(datasets[17], expected_data)
        else:
            self.fail("Could not generate APIResponse from test response")
