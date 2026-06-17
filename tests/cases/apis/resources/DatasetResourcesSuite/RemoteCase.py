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
        _url = f"{_testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/2024/1"
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

    def test_get_invalidinput(self):
        invalid_urls = {
            f"{self.base_url}/games/1NVAL1D_GAM3/datasets/2026/1",
            f"{self.base_url}/games/AQUALAB/datasets/1900/1",
            f"{self.base_url}/games/AQUALAB/datasets/2026/13",
        }
        for url in invalid_urls:
            with self.subTest(url=url):
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
            f"{self.base_url}/games/NONEXISTENT_GAME/datasets/2026/1",
            f"{self.base_url}/games/BLOOM/datasets/2020/1", # Bloom data doesn't start until well after 2020
            f"{self.base_url}/games/BLOOM/datasets/2024/1" # We have 2024 data for Bloom, but it starts in February.
        }
        for url in invalid_dataset_urls:
            with self.subTest(url=url):
                try:
                    response : APIResponse = APIRequest(url=url, request_type="GET", params={}, timeout=5).Execute(logger=Logger.std_logger)
                except Exception as err: # pylint: disable=broad-exception-caught
                    self.fail(str(err))
                else:
                    self.assertIsNotNone(response, f"No response from {url}")
                    self.assertEqual(response.Status, ResponseStatus.NOT_FOUND, f"Unexpected status from {url}: {response.Status}")
                    self.assertEqual(response.Type, RESTType.GET, f"Bad type from {url}")
                    self.assertIsNone(response.Value, f"Non-empty value from {url}")
