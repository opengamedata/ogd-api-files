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

class test_GameList(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url    : str
        cls.content : Optional[APIResponse]    = None

        cls.url    = f"{_testing_cfg.ExternEndpoint}/games"
        Logger.Log(f"Sending request to {cls.url}", logging.INFO)
        cls.content = APIRequest(url=cls.url, request_type="GET", timeout=30).Execute(logger=Logger.std_logger)

    def test_Responded(self):
        self.assertIsNotNone(self.content, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertEqual(self.content.Status, ResponseStatus.OK)
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
