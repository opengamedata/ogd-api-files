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
        _url = f"{self.base_url}/games/AQUALAB/datasets"
        # 1. Run request
        try:
            response : APIResponse = APIRequest(url=_url, request_type="GET", params={}, timeout=2).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
        # 2. Perform assertions
            self.assertIsNotNone(response, f"No response from {_url}")
            self.assertTrue(response.OK, f"Bad status from {_url}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsInstance(response.Value, dict, f"Bad value type from {_url}")
            if response.Value:
                self.assertIn("datasets", response.Value.keys(), "Response did not contain datasets")
                datasets = response.Value.get('datasets', [])
                self.assertIsInstance(datasets, list, "Response had null datasets")
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
