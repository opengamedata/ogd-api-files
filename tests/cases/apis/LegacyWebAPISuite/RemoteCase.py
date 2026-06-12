# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.utils.APIUtils import urljoin
from ogd.common.utils.Logger import Logger
# import locals
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config import t_config

class test_MonthlyGameUsage(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=t_config.settings)
        cls.base_url : str = f"{cls.testing_cfg.ExternEndpoint}"

        _level       = logging.DEBUG if cls.testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

    def test_monthlygameusage_get(self):
        _url = urljoin(base=self.base_url, url="getMonthlyGameUsage") 
        _params = {
            "game_id" : "AQUALAB"
        }
        try:
            result : APIResponse = APIRequest(url=_url, request_type="GET", params=_params).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
            self.assertIsNotNone(result, f"No response from {_url}")
            self.assertTrue(result.OK, f"Bad status from {_url}")
            self.assertEqual(str(result.Type), "GET", f"Bad type from {_url}")
            self.assertEqual(result.Message, "Hello! You GETted successfully!", f"Bad msg from {_url}")
            # check that return value is correct
            self.assertIsInstance(result.Value, dict)
            if result.Value:
                self.assertIn("game_id", result.Value.keys(), "Response did not contain game_id")
                self.assertEqual(result.Value.get("game_id", "NOT FOUND"), "AQUALAB")
                self.assertIn("sessions", result.Value.keys(), "Response did not contain sessions")
                sessions = result.Value.get('sessions', [])
                self.assertIsInstance(sessions, list)
                self.assertGreaterEqual(len(sessions), 2) # Aqualab should definitely have more than 2 months
                expected_data = {
                    'year': 2021,
                    'month': 5,
                    'total_sessions': 808
                }
                self.assertEqual(sessions[1], expected_data)

    def test_gamefileinfobymonth_get(self):
        _url = urljoin(base=self.base_url, url="getGameFileInfoByMonth") 
        _params = {
            "game_id" : "AQUALAB"
        }
        try:
            result : APIResponse = APIRequest(url=_url, request_type="GET", params=_params).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
            self.assertIsNotNone(result, f"No response from {_url}")
            self.assertTrue(result.OK, f"Bad status from {_url}")
            self.assertEqual(str(result.Type), "GET", f"Bad type from {_url}")
            self.assertEqual(result.Message, "Hello! You GETted successfully!", f"Bad msg from {_url}")
            # check that return value is correct
            self.assertIsInstance(result.Value, dict)
            if result.Value:
                # HACK: Currently, there's some mismatches in naming conventions between old and new, as well as in how we're parsing out what's what.
                # So, temporarily changing the "expected" from what would be truly ideal behavior, to what is expected given the shortcomings of the packages we're depending on.
                # This allows us to watch for regressions due to changes in the FileAPI code, and can be reverted when we get upstream improvements to the packages/what's actually named what on the server
                # expected_data['raw_file'] = expected_data['events_file']
                # expected_data['events_file'] = None
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
                self.assertEqual(set(result.Value.keys()), set(expected_data.keys()), msg="Mismatching keys between response and expected")
                for key, val in expected_data.items():
                    self.assertEqual(result.Value.get(key), val, msg=f"Mismatch for key {key}")

    @unittest.skip("This endpoint is not in use; needs access to database")
    def test_gameusagebymonth_get(self):
        _url = urljoin(base=self.base_url, url="getGameUsageByMonth") 
        params = {
            "game_id" : "AQUALAB",
            "year"    : 2024,
            "month"   : 1
        }
        try:
            result : APIResponse = APIRequest(url=_url, request_type="GET", params=params).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
            self.assertIsNotNone(result, f"No response from {_url}")
            self.assertTrue(result.OK, f"Bad status from {_url}")
            self.assertEqual(str(result.Type), "GET", f"Bad type from {_url}")
            self.assertEqual(result.Message, "Hello! You GETted successfully!", f"Bad msg from {_url}")
            # check that return value is correct
            self.assertIsInstance(result.Value, dict)

