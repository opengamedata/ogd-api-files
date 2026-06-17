# import libraries
import logging
from unittest import TestCase
# import ogd libraries
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.enums.ResponseStatus import ResponseStatus
from ogd.common.utils.Logger import Logger
# import locals
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

_testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
_level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
Logger.std_logger.setLevel(_level)

class RemoteCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testing_config = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
        cls.base_url : str = f"{_testing_cfg.ExternEndpoint}"

        _level = logging.DEBUG if cls.testing_config.Verbose else logging.INFO
        Logger.InitializeLogger(level=_level, use_logfile=False)

    def test_get(self):
        _url = f"{self.base_url}/games/AQUALAB/datasets/2024/1/manifest"
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
                expected_data = {
                    "game_id": "AQUALAB",
                    "dataset_id": "AQUALAB_20240101_to_20240131",
                    "population": {
                        "session_count": 5768,
                        "player_count": 5768,
                        "filters": {}
                    },
                    "game_state": {},
                    "events": None,
                    "features": None,
                    "versioning": {
                        "ogd_version": "UNKNOWN OGD VERSION",
                        "ogd_revision": "df72162",
                        "event_spec_version": "0.0.1"
                    },
                    "output": {
                        "all_events_file": "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_all-events.zip",
                        "game_events_file": "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_events.zip",
                        "all_features_file": None,
                        "sessions_file": "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_session-features.zip",
                        "players_file": "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_player-features.zip",
                        "population_file": "https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_population-features.zip"
                    },
                    "date_modified": "02/02/2024",
                    "start_date": "01/01/2024",
                    "end_date": "01/31/2024"
                }
                self.assertEqual(set(response.Value.keys()), set(expected_data.keys()), msg="Mismatching keys between response and expected")
                for key, val in expected_data.items():
                    with self.subTest(key=key, val=val):
                        self.assertEqual(response.Value.get(key), val, msg=f"Mismatching value for key {key}")

    def test_get_invalidinput(self):
        invalid_urls = {
            "/games/1NVAL1D_GAM3/datasets/2026/1/manifest",
            "/games/AQUALAB/datasets/1900/1/manifest",
            "/games/AQUALAB/datasets/2026/13/manifest",
        }
        for url in invalid_urls:
            with self.subTest(url=f"{self.base_url}{url}"):
                try:
                    response : APIResponse = APIRequest(url=url, request_type="GET", params={}, timeout=5).Execute(logger=Logger.std_logger)
                except Exception as err: # pylint: disable=broad-exception-caught
                    self.fail(str(err))
                else:
                    self.assertIsNotNone(response, f"No response from {url}")
                    self.assertEqual(response.Status, ResponseStatus.BAD_REQUEST, f"Unexpected status from {url}: {response.Status}")
                    self.assertEqual(response.Type, RESTType.GET, f"Bad type from {url}")
                    self.assertIsNone(response.Value, f"Non-empty value from {url}")

    def test_get_nonexistentdataset(self):
        invalid_dataset_urls = {
            "/games/NONEXISTENT_GAME/datasets/2026/1/manifest",
            "/games/BLOOM/datasets/2020/1/manifest", # Bloom data doesn't start until well after 2020
            "/games/BLOOM/datasets/2024/1/manifest" # We have 2024 data for Bloom, but it starts in February.
        }
        for url in invalid_dataset_urls:
            with self.subTest(url=f"{self.base_url}{url}"):
                try:
                    response : APIResponse = APIRequest(url=url, request_type="GET", params={}, timeout=5).Execute(logger=Logger.std_logger)
                except Exception as err: # pylint: disable=broad-exception-caught
                    self.fail(str(err))
                else:
                    self.assertIsNotNone(response, f"No response from {url}")
                    self.assertEqual(response.Status, ResponseStatus.NOT_FOUND, f"Unexpected status from {url}: {response.Status}")
                    self.assertEqual(response.Type, RESTType.GET, f"Bad type from {url}")
                    self.assertIsNone(response.Value, f"Non-empty value from {url}")
