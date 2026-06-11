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
        _url = f"{self.base_url}/games/AQUALAB/datasets/2026/1/population"
        try:
            response : APIResponse = APIRequest(url=_url, request_type="GET", params={}).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
            self.assertIsNotNone(response, f"No response from {_url}")
            self.assertTrue(response.OK, f"Bad status from {_url}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsInstance(response.Value, dict, f"Bad value type from {_url}")
            if response.Value:
                self.assertIn("columns", response.Value.keys(), "Response did not contain game_ids")
                self.assertIsNotNone(response.Value.get("game_ids"), "Response had null game_ids")
                known_cols = [
                    "PlayerCount", "SessionCount", "ActiveJobs",
                    "AppVersions", "ExperimentalCondition", "JobsCompleted",
                    "JobsCompleted-UniqueCount", "JobsCompleted-Names", "PlayedNonexperimentalVersion",
                    "SessionDiveSitesCount", "SessionID", "SwitchJobsCount",
                    "TimeInJournal", "TimeInJournal-Seconds", "TimeInJournal-Active",
                    "TimeInJournal-Active-Seconds", "TimeInJournal-Idle", "TimeInJournal-Idle-Seconds",
                    "TotalArgumentationTime", "TotalArgumentationTime-Seconds", "TotalArgumentationTime-Active",
                    "TotalArgumentationTime-Active-Seconds"
                ]
                for col in known_cols:
                    self.assertIn(col, response.Value.get("columns", []), f"No datasets for {col}")