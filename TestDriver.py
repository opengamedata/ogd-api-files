from tests.config.t_config import settings
from tests.config.FileAPITestConfig import FileAPITestConfig
from tests.cases.t_HelloAPI import t_HelloAPI

_cfg = FileAPITestConfig.FromDict(name="FileAPITestConfig", all_elements=settings, logger=None)
if _cfg.EnabledTests.get('HELLO', False):
    print("***\nRunning t_HelloAPI:")
    t_HelloAPI.RunAll()
    print("Done\n***")