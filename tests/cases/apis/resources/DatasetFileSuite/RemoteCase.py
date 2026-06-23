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
        _url = f"{self.testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/2026/1/population"
        try:
            response : APIResponse = APIRequest(url=_url, request_type="GET", params={}, timeout=5).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
            self.assertIsNotNone(response, f"No response from {_url}")
            self.assertTrue(response.OK, f"Bad status from {_url}: {response.Status}")
            self.assertEqual(response.Type, RESTType.GET, f"Bad type from {_url}")
            self.assertIsInstance(response.Value, dict, f"Bad value type from {_url}")
            if response.Value:
                self.assertIn("columns", response.Value.keys(), "Response did not contain columns")
                self.assertIsInstance(response.Value.get("columns"), list, "Response columns were not in a list")
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
                    with self.subTest(col=col):
                        self.assertIn(col, response.Value.get("columns", []), f"No datasets for {col}")

    def test_get_invalidinput(self):
        invalid_urls = {
            f"{self.testing_cfg.ExternEndpoint}/games/1NVAL1D_GAM3/datasets/2026/1/population",
            f"{self.testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/1900/1/population",
            f"{self.testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/2026/13/population",
            f"{self.testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/2026/1/invalidtype"
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
            f"{self.testing_cfg.ExternEndpoint}/games/NONEXISTENT_GAME/datasets/2026/1/population",
            f"{self.testing_cfg.ExternEndpoint}/games/BLOOM/datasets/2020/1/population", # Bloom data doesn't start until well after 2020
            f"{self.testing_cfg.ExternEndpoint}/games/BLOOM/datasets/2024/1/population" # We have 2024 data for Bloom, but it starts in February.
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
