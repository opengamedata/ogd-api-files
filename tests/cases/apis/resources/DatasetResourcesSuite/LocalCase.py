# import libraries
import logging
from json.decoder import JSONDecodeError
from unittest import TestCase
# import 3rd-party libraries
from flask import Flask
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
        # 1. Get testing config
        testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)

        _level     = logging.DEBUG if testing_cfg.Verbose else logging.INFO
        _str_level =       "DEBUG" if testing_cfg.Verbose else "INFO"
        Logger.InitializeLogger(level=_level, use_logfile=False)

        # 2. Set up local Flask app to run tests
        cls.application = Flask(__name__)
        cls.application.logger.setLevel(_level)
        cls.application.secret_key = b'thisisafakesecretkey'

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
        _url = "/games/AQUALAB/datasets/2024/1"
        # 1. Run request
        raw_response = self.server.get(_url)
        try:
            response = APIResponse.FromDict(all_elements=raw_response.json or {}, status=ResponseStatus(raw_response.status_code))
        except JSONDecodeError as err:
            self.fail(f"Could not parse {raw_response.text} to JSON!\n{err}")
        raw_response.close()
        # 2. Perform assertions
        if response:
            self.assertIsNotNone(response, f"No response from {_url}")
            self.assertTrue(response.OK, f"Bad status from {_url}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsInstance(response.Value, dict, f"Bad value type from {_url}")
            if response.Value:
                expected_data = {
                    "start_date":"01/01/2024",
                    "end_date":"01/31/2024",
                    "detectors_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/src/ogd/games/AQUALAB/detectors",
                    "events_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json",
                    "all_events_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_all-events.zip",
                    "events_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
                    "features_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/src/ogd/games/AQUALAB/features",
                    "combined_features_file":None,
                    "players_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%player-template%2Fdevcontainer.json",
                    "players_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_player-features.zip",
                    "players_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
                    "population_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_population-features.zip",
                    "population_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
                    "population_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%population-template%2Fdevcontainer.json",
                    "game_events_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_events.zip",
                    "sessions_codespace":	"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%session-template%2Fdevcontainer.json",
                    "sessions_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_session-features.zip",
                    "sessions_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
                }
                self.assertEqual(set(response.Value.keys()), set(expected_data.keys()), msg="Mismatching keys between response and expected")
                for key, val in expected_data.items():
                    with self.subTest(key=key, val=val):
                        self.assertEqual(response.Value.get(key), val, msg=f"Mismatching value for key {key}")
        else:
            self.fail("Could not generate APIResponse from test response")
