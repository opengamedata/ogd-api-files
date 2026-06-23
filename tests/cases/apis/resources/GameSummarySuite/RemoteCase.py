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

class RemoteCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)
        Logger.InitializeLogger(
            level       = logging.DEBUG if cls.testing_cfg.Verbose else logging.INFO,
            use_logfile = False
        )

    def test_get(self):
        _url = f"{self.testing_cfg.ExternEndpoint}/games/AQUALAB"
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
                expected_keys = {"game_id", "dataset_count", "average_sessions", "initial_dataset"}
                self.assertEqual(set(response.Value.keys()), expected_keys, "Response did not contain expected keys")
                self.assertEqual(response.Value.get("game_id"), "AQUALAB", "Incorrect game ID")
                self.assertEqual(response.Value.get("initial_dataset"), "2021-04-11", "Incorrect initial dataset date for AQUALAB")

    def test_get_invalidgame(self):
        _url = f"{self.testing_cfg.ExternEndpoint}/games/1NVAL1D_GAM3"
        # 1. Run request
        try:
            response : APIResponse = APIRequest(url=_url, request_type="GET", params={}, timeout=2).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        # 2. Perform assertions
        if response:
            self.assertIsNotNone(response, f"No response from {_url}")
            self.assertEqual(response.Status, ResponseStatus.BAD_REQUEST, f"Unexpected status from {_url}: {response.Status}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsNone(response.Value, f"Non-empty value from {_url}")
        else:
            self.fail("Could not generate APIResponse from test response")

    def test_get_nonexistentgame(self):
        _url = f"{self.testing_cfg.ExternEndpoint}/games/NONEXISTENT_GAME"
        # 1. Run request
        try:
            response : APIResponse = APIRequest(url=_url, request_type="GET", params={}, timeout=2).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        # 2. Perform assertions
        if response:
            self.assertIsNotNone(response, f"No response from {_url}")
            self.assertEqual(response.Status, ResponseStatus.NOT_FOUND, f"Unexpected status from {_url}: {response.Status}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsNone(response.Value, f"Non-empty value from {_url}")
        else:
            self.fail("Could not generate APIResponse from test response")
