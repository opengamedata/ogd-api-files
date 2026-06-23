# import libraries
import logging
from unittest import TestCase
# import ogd libraries
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.APIResponse import APIResponse
from ogd.common.utils.Logger import Logger
# import locals
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

class RemoteCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
        Logger.InitializeLogger(
            level       = logging.DEBUG if cls.testing_cfg.Verbose else logging.INFO,
            use_logfile = False
        )

    def test_get(self):
        _url = f"{self.testing_cfg.ExternEndpoint}/games/details"
        # 1. Run request
        try:
            response : APIResponse = APIRequest(url=_url, request_type="GET", params={}, timeout=2).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
        # 2. Perform assertions
            self.assertIsNotNone(response, f"No response from {_url}")
            self.assertTrue(response.OK, f"Bad status from {_url}: {response.Status}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsInstance(response.Value, dict, f"Bad value type from {_url}")
            if response.Value:
                known_games = {
                    "AQUALAB", "BACTERIA", "BALLOON", "BLOOM", "CRYSTAL",
                    "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE",
                    "ICECUBE", "JOURNALISM", "JOWILDER", "LAKELAND", "MAGNET",
                    "MASHOPOLIS", "PENGUINS", "PENNYCOOK", "SHADOWSPECT", "SHIPWRECKS",
                    "THERMOLAB", "THERMOVR", "TRANSFORMATION_QUEST", "WAVES",
                    "WEATHER_STATION", "WIND"
                }
                for game in known_games:
                    self.assertIn(game, response.Value.keys())
                aqualab_details = response.Value.get("AQUALAB")
                self.assertIsInstance(aqualab_details, dict, "AQUALAB details were not in dict form!")
                if aqualab_details:
                    expected_keys = {"game_id", "dataset_count", "average_sessions", "initial_dataset"}
                    self.assertEqual(set(aqualab_details.keys()), expected_keys, "AQUALAB details did not contain expected keys")
                    self.assertEqual(aqualab_details.get("game_id"), "AQUALAB", "Incorrect game ID")
                    self.assertEqual(aqualab_details.get("initial_dataset"), "2021-04-11", "Incorrect initial dataset date for AQUALAB")
