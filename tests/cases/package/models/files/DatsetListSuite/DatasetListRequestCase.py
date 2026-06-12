# import libraries
import logging
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from tests.config.t_config import settings
from package.src.ogd.apis.models.files.DatasetList import DatasetList, DatasetListRequest

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class DatasetListRequestCase(TestCase):
    """Test of the DatasetListRequest class.

    Theoretically, we ought to have multiple cases for the class, collected into a DatasetFileRequestSuite folder.
    However, given it's a single-use sort of thing, we're just doing a single test.
    
    Fixture:
    * Initialize a DatasetListRequest to request data from our reference remote dataset.
    
    Case Categories:
    * Execute(...) function
        * This is the only thing the class does.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `Feature` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        cls.base_url : str = settings.get("EXTERN_ENDPOINT", "127.0.0.1:5000")

    def test_Execute_all(self):
        request = DatasetListRequest(api_base_url=self.base_url, game_id="AQUALAB")
        result = request.Execute()
        self.assertIsInstance(result, DatasetList)
        if isinstance(result, DatasetList):
            self.assertEqual(len(result.Datasets), 100)

    def test_Execute_year(self):
        request = DatasetListRequest(api_base_url=self.base_url, game_id="AQUALAB", year=2025)
        result = request.Execute()
        self.assertIsInstance(result, DatasetList)
        if isinstance(result, DatasetList):
            self.assertEqual(len(result.Datasets), 12)
