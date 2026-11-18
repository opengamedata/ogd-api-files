# import libraries
import logging
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
from ogd.apis.models.files.GameSummary import GameSummary
# import locals
from src.ogd.apis.models.files.GameSummaries import GameSummaries, GameSummariesRequest
from tests.config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class GameSummariesRequestCase(TestCase):
    """Test of the GameSummariesRequest class.

    Theoretically, we ought to have multiple cases for the class, collected into a DatasetFileRequestSuite folder.
    However, given it's a single-use sort of thing, we're just doing a single test.
    
    Fixture:
    * Initialize a GameSummariesRequest to request data from our reference remote dataset.
    
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

    def test_Execute(self):
        request = GameSummariesRequest(api_base_url=self.base_url)
        result = request.Execute()
        self.assertIsInstance(result, GameSummaries)
        if isinstance(result, GameSummaries):
            self.assertEqual(len(result.Summaries.keys()), 27)
            for summary in result.Summaries.values():
                with self.subTest(summary=summary):
                    self.assertIsInstance(summary, GameSummary)
