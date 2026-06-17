# import libraries
import logging
from json.decoder import JSONDecodeError
from unittest import TestCase
# import 3rd-party libraries
from flask import Flask
# import ogd libraries
from ogd.apis.models.APIResponse import APIResponse, ResponseStatus
from ogd.apis.models.enums.RESTType import RESTType
from ogd.common.utils.Logger import Logger
# import locals
from src.configs.FileAPIConfig import FileAPIConfig
from src.apis.FileAPI import FileAPI
from tests.FileAPITestConfig import FileAPITestConfig
from tests.config.t_config import settings

class LocalCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Get testing config
        testing_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=settings)

        _level     = logging.DEBUG if testing_cfg.Verbose else logging.INFO
        _str_level =       "DEBUG" if testing_cfg.Verbose else "INFO"
        Logger.InitializeLogger(level=_level, use_logfile=False)

        # 2. Set up local Flask app to run tests
        cls.application = Flask(__name__)
        cls.application.logger.setLevel(_level)
        cls.application.secret_key = b'thisisafakesecretkey'

        _server_cfg_elems = {
            "API_VERSION"   : "0.0.0-Testing",
            "DEBUG_LEVEL"   : _str_level,
            "FILE_LIST_URL" : 'https://opengamedata.fielddaylab.wisc.edu/data/file_list.json',
            "BIGQUERY_GAME_MAPPING" : {}
        }
        _server_cfg = FileAPIConfig.FromDict(name="HelloAPITestServer", unparsed_elements=_server_cfg_elems)
        FileAPI.register(app=cls.application, settings=_server_cfg)

        cls.server = cls.application.test_client()

    def test_get(self):

        _url = "/games/AQUALAB/datasets/2026/1/population"
        # 1. Run request
        raw_response = self.server.get(_url)
        try:
            response = APIResponse.FromDict(all_elements=raw_response.json or {}, status=ResponseStatus(raw_response.status_code))
        except JSONDecodeError as err:
            self.fail(f"Could not parse {raw_response.text} to JSON!\n{err}")
        raw_response.close()
        # 2. Perform assertions
        if response:
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
        else:
            self.fail("Could not generate APIResponse from test response")

    def test_get_invalidinput(self):
        invalid_urls = {
            "/games/1NVAL1D_GAM3/datasets/2026/1/population",
            "/games/AQUALAB/datasets/1900/1/population",
            "/games/AQUALAB/datasets/2026/13/population",
            "/games/AQUALAB/datasets/2026/1/invalidtype"
        }
        for url in invalid_urls:
            with self.subTest(url=url):
                # 1. Run request
                raw_response = self.server.get(url)
                try:
                    response = APIResponse.FromDict(all_elements=raw_response.json or {}, status=ResponseStatus(raw_response.status_code))
                except JSONDecodeError as err:
                    self.fail(f"Could not parse {raw_response.text} to JSON!\n{err}")
                raw_response.close()
                # 2. Perform assertions
                if response:
                    self.assertIsNotNone(response, f"No response from {url}")
                    self.assertEqual(response.Status, ResponseStatus.BAD_REQUEST, f"Unexpected status from {url}: {response.Status}")
                    self.assertEqual(response.Type, RESTType.GET, f"Bad type from {url}")
                    self.assertIsNone(response.Value, f"Non-empty value from {url}")
                else:
                    self.fail("Could not generate APIResponse from test response")

    def test_get_nonexistentdataset(self):
        invalid_dataset_urls = {
            "/games/NONEXISTENT_GAME/datasets/2026/1/population",
            "/games/BLOOM/datasets/2020/1/population", # Bloom data doesn't start until well after 2020
            "/games/BLOOM/datasets/2024/1/population" # We have 2024 data for Bloom, but it starts in February.
        }
        for url in invalid_dataset_urls:
            with self.subTest(url=url):
                # 1. Run request
                raw_response = self.server.get(url)
                try:
                    response = APIResponse.FromDict(all_elements=raw_response.json or {}, status=ResponseStatus(raw_response.status_code))
                except JSONDecodeError as err:
                    self.fail(f"Could not parse {raw_response.text} to JSON!\n{err}")
                raw_response.close()
                # 2. Perform assertions
                if response:
                    self.assertIsNotNone(response, f"No response from {url}")
                    self.assertEqual(response.Status, ResponseStatus.NOT_FOUND, f"Unexpected status from {url}: {response.Status}")
                    self.assertEqual(response.Type, RESTType.GET, f"Bad type from {url}")
                    self.assertIsNone(response.Value, f"Non-empty value from {url}")
                else:
                    self.fail("Could not generate APIResponse from test response")
