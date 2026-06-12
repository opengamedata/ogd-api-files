# import libraries
import logging
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from tests.config.t_config import settings
from package.src.ogd.apis.models.files.DatasetFile import DatasetFile, DatasetFileRequest

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class DatasetFileRequestCase(TestCase):
    """Test of the DatasetFileRequest class.

    Theoretically, we ought to have multiple cases for the class, collected into a DatasetFileRequestSuite folder.
    However, given it's a single-use sort of thing, we're just doing a single test.
    
    Fixture:
    * Initialize a DatasetFileRequest to request data from our reference remote dataset.
    
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

    def test_Execute_sessions(self):
        request = DatasetFileRequest(api_base_url=self.base_url, game_id="AQUALAB", year=2025, month=6, file_type="session")
        result = request.Execute()
        self.assertIsInstance(result, DatasetFile)
        if isinstance(result, DatasetFile):
            self.assertEqual(len(result.Rows), 3315)

    def test_Execute_players(self):
        request = DatasetFileRequest(api_base_url=self.base_url, game_id="AQUALAB", year=2025, month=6, file_type="player")
        result = request.Execute()
        self.assertIsInstance(result, DatasetFile)
        if isinstance(result, DatasetFile):
            self.assertEqual(len(result.Rows), 100)

    def test_Execute_population(self):
        request = DatasetFileRequest(api_base_url=self.base_url, game_id="AQUALAB", year=2025, month=6, file_type="population")
        result = request.Execute()
        self.assertIsInstance(result, DatasetFile)
        if isinstance(result, DatasetFile):
            self.assertEqual(len(result.Rows), 1)
