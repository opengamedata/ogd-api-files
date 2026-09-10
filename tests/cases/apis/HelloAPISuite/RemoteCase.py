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
        urls = [f"{self.testing_config.ExternEndpoint}/", f"{self.testing_config.ExternEndpoint}/hello"]
        for url in urls:
            with self.subTest(url=url):
                try:
                    response : APIResponse = APIRequest(url=url, request_type="GET", params={}).Execute(logger=Logger.std_logger)
                except Exception as err: # pylint: disable=broad-exception-caught
                    self.fail(str(err))
                else:
                    self.assertIsNotNone(response, f"No response from {url}")
                    self.assertTrue(response.OK, f"Bad status from {url}: {response.Status}")
                    self.assertEqual(str(response.Type), "GET", f"Bad type from {url}")
                    self.assertIsNone(response.Value, f"Bad val from {url}")
                    self.assertEqual(response.Message, "Hello! You GETted successfully!", f"Bad msg from {url}")
