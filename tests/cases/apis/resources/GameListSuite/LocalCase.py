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
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse, ResponseStatus
from ogd.common.utils.Logger import Logger
# import locals
from src.configs.FileAPIConfig import FileAPIConfig
from src.apis.FileAPI import FileAPI
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

class test_GameList_local(TestCase):
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

        cls.url    = f"/games"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.result = cls.server.get(cls.url)
        if cls.result is not None:
            try:
                _raw = cls.result.json
            except JSONDecodeError as err:
                print(f"Could not parse {cls.result.text} to JSON!\n{err}")
            else:
                cls.content = APIResponse.FromDict(all_elements=_raw or {}, status=ResponseStatus(cls.result.status_code))

    @classmethod
    def tearDownClass(cls):
        if cls.result is not None:
            cls.result.close()

    def test_Responded(self):
        self.assertIsNotNone(self.result, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.result is not None:
            self.assertEqual(self.result.status_code, 200)
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
