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

        _url = "/games"
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
                self.assertIn("game_ids", response.Value.keys(), "Response did not contain game_ids")
                self.assertIsNotNone(response.Value.get("game_ids"), "Response had null game_ids")
                known_games = [
                    "AQUALAB", "BACTERIA", "BALLOON", "BLOOM", "CRYSTAL",
                    "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE",
                    "ICECUBE", "JOURNALISM", "JOWILDER", "LAKELAND", "MAGNET",
                    "MASHOPOLIS", "PENGUINS", "PENNYCOOK", "SHADOWSPECT", "SHIPWRECKS",
                    "THERMOLAB", "THERMOVR", "TRANSFORMATION_QUEST", "WAVES",
                    "WEATHER_STATION", "WIND"
                ]
                for game in known_games:
                    self.assertIn(game, response.Value.get("game_ids", []), f"No datasets for {game}")
        else:
            self.fail("Could not generate APIResponse from test response")

