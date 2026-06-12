# import libraries
import logging
from unittest import TestCase
# import ogd libraries
from ogd.apis.models.APIRequest import APIRequest
from ogd.apis.models.APIResponse import APIResponse
from ogd.common.utils.Logger import Logger
# import locals
from tests.config import t_config
from tests.FileAPITestConfig import FileAPITestConfig

class test_Hello(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testing_config = FileAPITestConfig.FromDict(name="FileAPITestConfig", unparsed_elements=t_config.settings)

        _level       = logging.DEBUG if cls.testing_config.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

    def test_get(self):
        _url = f"{self.testing_config.ExternEndpoint}/hello"
        try:
            result : APIResponse = APIRequest(url=_url, request_type="GET", params={}).Execute(logger=Logger.std_logger)
        except Exception as err: # pylint: disable=broad-exception-caught
            self.fail(str(err))
        else:
            self.assertIsNotNone(result, f"No response from {_url}")
            self.assertTrue(result.OK, f"Bad status from {_url}")
            self.assertEqual(str(result.Type), "GET", f"Bad type from {_url}")
            self.assertIsNone(result.Value, f"Bad val from {_url}")
            self.assertEqual(result.Message, "Hello! You GETted successfully!", f"Bad msg from {_url}")
