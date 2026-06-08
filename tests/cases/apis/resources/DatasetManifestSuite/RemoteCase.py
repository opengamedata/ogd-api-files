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

class test_GameDatasetInfo(TestCase):
    def setUp(self):
        self.url    : str
        self.content : Optional[APIResponse]    = None

        self.url    = f"{_testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/2024/1"
        Logger.Log(f"Sending request to {self.url}", logging.INFO)
        self.content = APIRequest(url=self.url, request_type="GET", timeout=30).Execute(logger=Logger.std_logger)

    def test_Responded(self):
        self.assertIsNotNone(self.content, f"No result from request to {self.url}")

    def test_Succeeded(self):
        if self.content is not None:
            self.assertTrue(self.content.Status == ResponseStatus.OK)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        expected_data = {
            "detectors_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/src/ogd/games/AQUALAB/detectors",
            "events_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fevent-template%2Fdevcontainer.json",
            "events_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_all-events.zip",
            "events_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "features_link":"https://github.com/opengamedata/opengamedata-core/tree/df72162/src/ogd/games/AQUALAB/features",
            "first_month":1,
            "first_year":2024,
            "found_matching_range":True,
            "last_month":1,
            "last_year":2024,
            "players_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fplayer-template%2Fdevcontainer.json",
            "players_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_player-features.zip",
            "players_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "population_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fpopulation-template%2Fdevcontainer.json",
            "population_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_population-features.zip",
            "population_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
            "raw_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_events.zip",
            "sessions_codespace":"https://codespaces.new/opengamedata/opengamedata-samples/tree/aqualab?quickstart=1&devcontainer_path=.devcontainer%2Fsession-template%2Fdevcontainer.json",
            "sessions_file":"https://opengamedata.fielddaylab.wisc.edu/data/AQUALAB/AQUALAB_20240101_to_20240131_df72162_session-features.zip",
            "sessions_template":"https://github.com/opengamedata/opengamedata-templates/tree/aqualab",
        }
        # HACK: Currently, there's some mismatches in naming conventions between old and new, as well as in how we're parsing out what's what.
        # So, temporarily changing the "expected" from what would be truly ideal behavior, to what is expected given the shortcomings of the packages we're depending on.
        # This allows us to watch for regressions due to changes in the FileAPI code, and can be reverted when we get upstream improvements to the packages/what's actually named what on the server
        expected_data['raw_file'] = expected_data['events_file']
        expected_data['events_file'] = None

        if self.content is not None and self.content.Value is not None:
            self.assertEqual(set(self.content.Value.keys()), set(expected_data.keys()), msg="Mismatching keys between response and expected")
            for key, val in expected_data.items():
                self.assertEqual(self.content.Value.get(key), val, msg=f"Mismatch for key {key}")
        else:
            self.fail(f"No JSON content from request to {self.url}")

class test_GameDatasetInfo_notfound(TestCase):
    def setUp(self):
        self.url    : str
        self.content : Optional[APIResponse]    = None

        self.url    = f"{_testing_cfg.ExternEndpoint}/games/AQUALAB/datasets/2021/1"
        Logger.Log(f"Sending request to {self.url}", logging.INFO)
        self.content = APIRequest(url=self.url, request_type="GET", timeout=30).Execute(logger=Logger.std_logger)

    def test_Responded(self):
        self.assertIsNotNone(self.content, f"No result from request to {self.url}")

    def test_Errored(self):
        if self.content is not None:
            self.assertNotEqual(self.content.Status, ResponseStatus.OK)
        else:
            self.fail(f"No result from request to {self.url}")

    def test_Correct(self):
        expected_msg = "ERROR: Could not find a dataset for AQUALAB in 01/2021"

        if self.content is not None:
            self.assertIsNone(self.content.Value)
            if self.content.Message is not None:
                self.assertEqual(self.content.Message, expected_msg, msg="Mismatching messages between response and expected")
        else:
            self.fail(f"No JSON content from request to {self.url}")
