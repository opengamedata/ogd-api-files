from tests.config.t_config import settings
from tests.schemas.TestConfigSchema import TestConfigSchema
from tests.cases.HelloAPI.t_HelloAPI import t_HelloAPI

_cfg = TestConfigSchema.FromDict(name="TestDriverConfig", all_elements=settings, logger=None)
if _cfg.EnabledTests.get('HELLO', False):
    print("***\nRunning t_HelloAPI:")
    t_HelloAPI.RunAll()
    print("Done\n***")